#!/usr/bin/env bash
# usage: ./run_tests.sh my.exe data.txt [-s N]

set -u

ONLY=""
POS=()

while [ $# -gt 0 ]; do
    case "$1" in
        -s)
            if [ $# -lt 2 ]; then
                echo "Error: -s requires an argument" >&2
                exit 2
            fi
            ONLY="$2"
            shift 2
            ;;
        -s*)
            ONLY="${1#-s}"
            shift
            ;;
        --)
            shift
            while [ $# -gt 0 ]; do POS+=("$1"); shift; done
            ;;
        -*)
            echo "Unknown option: $1" >&2
            exit 2
            ;;
        *)
            POS+=("$1")
            shift
            ;;
    esac
done

if [ "${#POS[@]}" -ne 2 ]; then
    echo "Usage: $0 <executable> <data.txt> [-s N]" >&2
    exit 2
fi

EXE="${POS[0]}"
DATA="${POS[1]}"

if ! [[ "$ONLY" =~ ^[0-9]*$ ]]; then
    echo "Error: -s N must be a positive integer" >&2
    exit 2
fi

if [ ! -x "$EXE" ]; then
    echo "Error: '$EXE' is not executable" >&2
    exit 2
fi
if [ ! -f "$DATA" ]; then
    echo "Error: '$DATA' not found" >&2
    exit 2
fi
if ! command -v valgrind >/dev/null 2>&1; then
    echo "Error: valgrind not found in PATH" >&2
    exit 2
fi

DATA_DIR="$(cd "$(dirname "$DATA")" && pwd)"
DATA_BASE="$(basename "$DATA")"

# Разбираем файл на тесты.
awk -v dir="$DATA_DIR" -v base="$DATA_BASE" '
BEGIN { n = 0; part = "in"; in_test = 0 }
/^----$/ {
    if (part == "in") { part = "out"; next }
}
/^====$/ {
    part = "in"; in_test = 0; next
}
{
    if (!in_test) { n++; in_test = 1 }
    fname = dir "/" base ".t" n "." part
    print > fname
}
' "$DATA"

NUM=0
for f in "$DATA_DIR/$DATA_BASE".t*.in; do
    [ -e "$f" ] || continue
    NUM=$((NUM + 1))
done

if [ "$NUM" -eq 0 ]; then
    echo "No tests found in '$DATA'" >&2
    exit 2
fi

# Формируем список тестов для прогона
if [ -n "$ONLY" ]; then
    if [ "$ONLY" -lt 1 ] || [ "$ONLY" -gt "$NUM" ]; then
        echo "Error: test #$ONLY not found (1..$NUM)" >&2
        exit 2
    fi
    TESTS=("$ONLY")
else
    TESTS=()
    for i in $(seq 1 "$NUM"); do
        TESTS+=("$i")
    done
fi

PASS=0
FAIL=0

VALGRIND_OPTS=(
    --error-exitcode=42
    --leak-check=full
    --errors-for-leak-kinds=definite,indirect
    --quiet
)

for i in "${TESTS[@]}"; do
    IN="$DATA_DIR/$DATA_BASE.t$i.in"
    EXP="$DATA_DIR/$DATA_BASE.t$i.out"

    if [ ! -f "$IN" ]; then
        echo "Test $i: missing input, skipping" >&2
        continue
    fi
    if [ ! -f "$EXP" ]; then
        : > "$EXP"
    fi

    VG_LOG="$(mktemp)"
    OUT_FILE="$(mktemp)"
    valgrind "${VALGRIND_OPTS[@]}" "$EXE" < "$IN" >"$OUT_FILE" 2>"$VG_LOG"
    VG_RC=$?

    # EXPECTED="$(cat "$EXP")"
    # ACTUAL="$(cat "$OUT_FILE")"
    # remove all spaces from end of lines
    EXPECTED="$(sed -e 's/\r$//' -e 's/[[:space:]]*$//' "$EXP")"
    ACTUAL="$(sed -e 's/\r$//' -e 's/[[:space:]]*$//' "$OUT_FILE")"
    
    # echo "  --- expected (raw) ---"
    # printf '%s\n' "$EXPECTED" | cat -A | sed 's/^/  /'
    # echo "  --- actual (raw) ---"
    # printf '%s\n' "$ACTUAL" | cat -A | sed 's/^/  /'

    OUT_OK=1
    if [ "$ACTUAL" != "$EXPECTED" ]; then
        OUT_OK=0
    fi

    ERRORS=$(grep -E "ERROR SUMMARY: [0-9]+ errors" "$VG_LOG" | tail -n1 | grep -oE '[0-9]+' | head -n1)
    LEAKS=$(grep -E "definitely lost|indirectly lost" "$VG_LOG" | grep -oE '[0-9,]+ bytes' | tr -d ',' | awk '{s+=$1} END{print s+0}')
    : "${ERRORS:=unknown}"
    : "${LEAKS:=0}"

    VG_OK=1
    if [ "$VG_RC" -ne 0 ]; then
        VG_OK=0
    fi
    if [ "$ERRORS" != "0" ] && [ "$ERRORS" != "unknown" ]; then
        VG_OK=0
    fi
    if [ "$LEAKS" -ne 0 ]; then
        VG_OK=0
    fi

    if [ "$OUT_OK" -eq 1 ] && [ "$VG_OK" -eq 1 ]; then
        echo "Test $i: OK"
        PASS=$((PASS + 1))
    else
        echo "Test $i: FAIL"
        if [ "$OUT_OK" -eq 0 ]; then
            echo "  --- input ($IN) ---"
            sed 's/^/  /' "$IN"
            echo "  --- expected ($EXP) ---"
            printf '%s\n' "$EXPECTED" | sed 's/^/  /'
            echo "  --- actual ---"
            printf '%s\n' "$ACTUAL" | sed 's/^/  /'
        fi
        if [ "$VG_OK" -eq 0 ]; then
            echo "  --- valgrind (rc=$VG_RC, errors=$ERRORS, leaked_bytes=$LEAKS) ---"
            sed 's/^/  /' "$VG_LOG"
        fi
        FAIL=$((FAIL + 1))
    fi

    rm -f "$VG_LOG" "$OUT_FILE"
done

echo
echo "Passed: $PASS, Failed: $FAIL, Total: ${#TESTS[@]}"
[ "$FAIL" -eq 0 ]
