/* LAB ASSIGNMENT 2:

  The goal of this lab assignment is that you learn how to implement
  a "while" loop in assembly and how to specify addresses 
  
  Task: 
    - Implement a function that counts the number of lowercase 
    characters in a string. The string is zero terminated, i.e., the last 
    character is a character with the ASCII code 0. - ASCII table can be 
	found at http://www.asciitable.com/
	- Rememeber to test if the input string "inputString" is not empty 
	before accessing the string elements
	- Note that you are not allowed to create new variables besides
	"inputString" and "numChar", and you should not need more than 4 
	registers eax, ebx, ecx, edx
    - To test your code, see the the file main.c
	- Submit ONLY the file lab2.c!

  Remember to write your student ID and name in the marked places in
  this file.
  
*/

char *name = "Your name";
char *studentID = "Your student ID";

/* You are asked to implement this function */
int countLowerCaseCharacter(char *inputString)
{
	int numChar = -1;
	__asm
	{
		push eax
		push ebx
		push ecx
		push edx
		
		// BEGIN YOUR CODE HERE


		// END YOUR CODE HERE
		
		pop edx
		pop ecx
		pop ebx
		pop eax
		
	}
	return numChar;
}

