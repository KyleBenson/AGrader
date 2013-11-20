#include <stdio.h>

extern char* name;
extern char* studentID;
extern int countLowerCaseCharacter();

int main()
{
	int count;
    char* string1 = NULL;
	char* string2 = "QWERTY";
	char* string3 = "AAZZFF2134a94z271ZAF";
	char* string4 = "ZAzdDF2134a94z271ZrA";

	//printf("Name: %s\n", name);
	//printf("StudentID: %s\n\n", studentID);

	//Uncomment test case(s) to test.

	//Test 1
    count = countLowerCaseCharacter(string1);
	printf("%d\n", count);
  
	//Test 2
    count = countLowerCaseCharacter(string2);
	printf("%d\n", count);
   
	//Test 3
    count = countLowerCaseCharacter(string3);
	printf("%d", count);
 
	//Test 4
    count = countLowerCaseCharacter(string4);
	printf ("%d\n", count);

	return 0;
}
