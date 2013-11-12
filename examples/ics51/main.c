#include <stdio.h>

extern char *yourName;
extern char *studentID;
extern int numTests;
extern void bit_operations(unsigned long inputDWord, unsigned long *outputDWord);

void main()
{
	unsigned long myVar;
	unsigned long tmpValue;
    unsigned long shouldBe;
	int i;

	printf("NAME: %s\n\n", yourName);

	// Test Generator (up to four)
	if( numTests > 4 )
		numTests = 4;

    // Expected values
	for( i = 0; i < numTests; i++){
		switch( i ){
			case 0: myVar = 0xaa00a1f2;
                shouldBe = 0x55aa033c;
				break;
			case 1: myVar = 0x0c0c0c0c;
                shouldBe = 0x30a602c3;
				break;
			case 2: myVar = 0xa0b0c0d0;
                shouldBe = 0x051a023c;
				break;
			case 3: myVar = 0x80ff85f0;
                shouldBe = 0x0155033c;
				break;
			default: myVar = 0xaa00a1f2;
                shouldBe = 0x55aa033c;
        }

        printf("RUNNING TEST %d :: ", i+1);
		printf("INPUT BYTES: %X\n\n", myVar);

        tmpValue = myVar;

        bit_operations(myVar, &tmpValue);
        printf("RESULT -> SHOULD BE: %X - is: %X\n\n", shouldBe, tmpValue);
    }
}