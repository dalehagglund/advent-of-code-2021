// An alloy model to solve Day 8 of Advent of Code 2021

// A theme suitable for this model is found in 08_alloy.thm

// In this model, a "wire" is an integer that corresponds directly
// to the desired segment to be lit up for any Digit whose encoding
// contains that wire. So, an unscrambled display,
//
// 1 -> A
// 2 -> B
//
// and so on.

//
// elements of Lit correspond to the segments observed on the 
// scrambled displays. For each segment s, s.v will be the 
// the wire that is connected to that segment
//
sig Lit { v: Int }
one sig A, B, C, D, E, F, G extends Lit {}

//
// Digits define the mapping of desired output digits to "wires", ie, 
// a digit defines its encoding onto a standard unscrambled display.
//
sig Digit { wires: set (1 + 2 + 3 + 4 + 5 + 6 + 7) }
one sig Zero, One, Two, Three, Four, Five, Six, Seven, Eight, Nine extends Digit {}

//
// The Display describes the output part of the problem, and the solution:
//
// - Display.d1, ... are the observed Lit segments for output digits 1-4
// - Display.v1, ... are the decoded digits that would appear if the
//   display weren't scrambled.
//
one sig Display {
	d4: set Lit,
	d3: set Lit,
	d2: set Lit,
	d1: set Lit,
	v1: set Digit,
	v2: set Digit,
	v3: set Digit,
	v4: set Digit,
}

fact "each lit segment maps to a single wire" {
	Lit.v in 1 + 2 + 3 + 4 + 5 + 6 + 7
	all disj lit1, lit2: Lit | lit1.v != lit2.v
}

fact "what wires should be used for each digit" {
	One.wires   = 3 + 6
	Seven.wires = 1 + 3 + 6
	Four.wires  = 2 + 3 + 4 + 6

	Two.wires   = 1 + 3 + 4 + 5 + 7 
	Three.wires = 1 + 3 + 4 + 6 + 7
	Five.wires  = 1 + 2 + 4 + 6 + 7

	Zero.wires  = 1 + 2 + 3 + 5 + 6 + 7
	Six.wires   = 1 + 2 + 4 + 5 + 6 + 7
	Nine.wires  = 1 + 2 + 3 + 4 + 6 + 7

	Eight.wires = 1 + 2 + 3 + 4 + 5 + 6 + 7
}

pred single[segs: set Lit, d: Digit] {
	segs.v = d.wires
}

pred triple[segs: set Lit, d1: Digit, d2: Digit, d3: Digit] {
	segs.v = d1.wires
	or segs.v = d2.wires
	or segs.v = d3.wires	
}

//
// define the input information: what are 10 distinct patterns observed.
// these constraints are sufficient to fully define Lit.v
//

fact "distinct segment patterns" {
	// ab     ab.....     1
	// dab    ab.d...     7
	// eafb   ab..ef.     4

	single[A + B, One]
	single[A + B + D, Seven]
	single[A + B + E + F, Four]

	// cdfbe  .bcdef.     2, 3 5
	// gcdfa  a.cd.fg     "
	// fbcad  abcd.f.     "

	triple[B + C + D + E + F, Two, Three, Five]
	triple[A + C + D + F + G, Two, Three, Five]
	triple[A + B + C + D + F, Two, Three, Five]

	// cefabd abcdef.     0, 6, 9
	// cdfgeb .bcdefg     "
	// cagedb abcde.g     "

	triple[A + B + C + D + E + F, Zero, Six, Nine]
	triple[B + C + D + E + F + G, Zero, Six, Nine]
	triple[A + B + C + D + E + G, Zero, Six, Nine]

	// acedgfb abcdefg     8

	single[A + B + C + D + E + F + G, Eight]
}

fun find_digit[segs: set Lit]: Digit {
	{ d: Digit | segs.v = d.wires }
}

// describe the state of the output panel, and 
// find the correct output digit.

fact "panel readings" {
	Display.d1 = C + D + F + E + B
	Display.d2 = F + C + A + D + B
	Display.d3 = C + D + F + E + B
	Display.d4 = C + D + B + A + F

	Display.v1 = find_digit[Display.d1]
	Display.v2 = find_digit[Display.d2]
	Display.v3 = find_digit[Display.d3]
	Display.v4 = find_digit[Display.d4]
}

run {}
