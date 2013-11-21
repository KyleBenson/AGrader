#include <stdio.h>

unsigned long MIRROR_BYTE( unsigned long inputDWord );
unsigned long SET_BITS( unsigned long inputDWord );
unsigned long INVERT_BITS( unsigned long inputDWord );
unsigned long COUNT_ONES( unsigned long inputDWord );

/*
    --- LAB ASSIGNMENT 4 ---
	
	The goal of this assigment is to implement procedures and 
    procedure calls in assembly as well as perform logic operations on bits.

	TASK:
	- Implement a function that takes an input of size dword (4 bytes). From this
    function you must call FOUR separate procedures to manipulate the input bytes. Each 
    parameter takes as its input the same dword input and will return a modified version
    of one of the input bytes. After the 4 functions are called the four resulting bytes
    need to be stored in one dword which is the second parameter to the original function.

	IMPORTANT NOTES:
    - If your program fails to build, you will get zero. So please make sure it at
    least builds succesfully.
    - Regarding the runtime errors (errors when the program run), you may get partial 
    credits for your program depending on the test cases that your program succesfully
    passes. Also, commenting major blocks of code helps the graders to understand
    what you do and so may give you some credits.
    - You are not allowed to change anything of this file except for putting you 
    assembly codes in the space provided.
    - Remember to fill in your name, student ID, and UCInetID below.
    - Please submit ONLY lab4.c file for grading.
*/

char *yourName = "XXXXXXX";
char *studentID = "12345678";  
int numTests = 4;  // change this to increase test cases. ( 1, 2, 3 or 4 )

/*
    0) "bit_operations" is the function which will call the other 4 functions. 
	Before you return from this function don't forget to store the resulting 4 bytes 
	into the address pointed by outputDWord                                    
*/
__declspec(naked) 
long bit_operations(unsigned long inputDWord, unsigned long *outputDWord)
{
    __asm{
    // Start your code here
    

	
    // End your code here
    ret
    }
}


/*
    1) "SET_BITS" function takes 4 bytes (dword) as input. Take byte 0 and determine the 
    output byte as follows: 
	- Given input: 0x01ABCDEF, take byte 0: 11101111 (0xEF).
    - If bit at position 7 (leftmost) of byte 0 == 1 (which in this case it is) then 
    set the middle 4 bits to 1 and the rest to 0: 00111100. 
    - Else set the middle 4 bits to 0 and the rest to 1: 11000011.   
*/
__declspec(naked) 
unsigned long SET_BITS( unsigned long inputDWord )
{
    __asm{
    // Start your code here
	
	
	
    // End your code here
    ret
    }
}


/*
    2) "COUNT_ONES" function takes the same 4 bytes(dword) as input. It takes byte 1 and 
	counts the number of ones (bits that have a 1). 
	- E.g. given input: 0x01ABCDEF, take byte 1: 11001101 (0xCD). Return 0x05 (00000101).
*/
__declspec(naked) 
unsigned long COUNT_ONES( unsigned long inputDWord )
{
    __asm{
	// Start your code here
	
	
	
	// End your code here
    ret
    }
}


/* 
    3) "INVERT_BITS" function takes the same 4 bytes(dword) as input. It will invert the 
	value of the bits located in positions 7,5,3,1 of byte 2 in the input dword.
    E.g. Given input: 0x01ABCDEF, take byte 2: 10101011 (0xAB), invert values of bits 
	at positions 7,5,3,1 and return 00000001.
*/
__declspec(naked) 
unsigned long INVERT_BITS( unsigned long inputDWord )
{
    __asm{
	// Start your code here
    
	
	
	// End your code here
    ret
    }
}


/*
    4. "MIRROR_BYTE" function takes the same 4 bytes(dword) as input and mirrors the value 
	of byte 3 (leftmost).
    E.g. For a byte like 10110111, the mirrored byte value is 11101101.
*/
__declspec(naked) 
unsigned long MIRROR_BYTE( unsigned long inputDWord )
{
    __asm{
	// Start your code here
    
	
	
	// End your code here
    ret
    }
}


