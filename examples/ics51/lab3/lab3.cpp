/*
--- LAB ASSIGNMENT 3 ---

TASK:
  - You are given a sorted in ascending order input array, its size (1<=size<=100),
    and a key to search for. You're requested to write a function to search the key
    in the array using the binary search approach, which is explained here:

    http://www.geocities.com/cool_ranju/bsearch.html
	
    Implement the function below:
  
    int  binarySearch (int* arr, int arrSize, int key, int* count)
	
	  arr: an int pointer pointing to the first int of the array
	  arrSize: size of the array
	  key: an int to search for
	  count: an int pointer to save the count

    (1) The function should return the position of the key if the search is 
	successfuly or -1 if the search fails
	(2) The function should also count the number of comparisons done during the search, 
	which should be copied into "count" variable.

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
  - Please submit ONLY lab3.c file for grading.
*/

char* name = "Your Name";
char* studentID = "Student ID";
char* netID = "UCInetID";


int  binarySearch (int* arr, int arrSize, int key, int* count)
{
	int result=-1;
	__asm
    {
		push esi;
		push edi;
		push eax;
		push ebx;
		push ecx;
		push edx;
		
		// START CODING HERE
		
	
		// END CODING HERE

		pop edx;
		pop ecx;
		pop ebx;
		pop eax;
		pop edi;
		pop esi;
	}
	return result;
}

