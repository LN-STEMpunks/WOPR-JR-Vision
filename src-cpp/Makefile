OUT=main.out

BFLAGS=$(shell pkg-config --cflags opencv)
AFLAGS=$(shell pkg-config --libs opencv)

build: *.cpp
	g++ ${BFLAGS} -std=c++11 *.cpp -o ${OUT} ${AFLAGS}

run: build
	./${OUT}