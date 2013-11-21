#include <cstdlib>
#include <fstream>
#include <iostream>

extern char* name;
extern char* studentID;
extern char* netID;

extern int binarySearch(int* arr, int arrSize, int key, int* count);
//don't declare as extern if we want to compile without the student submission
//int binarySearch(int* arr, int arrSize, int key, int* count);

//more points for getting correct index than in the same # of iterations
int resultPoints = 15, countPoints = 5;

using namespace std;

int  binarySearchInC(int* arr, int arrSize, int key, int* count)
{
  int result=-1;
  int low =0;
  int high = arrSize-1;
  int middle;
  *count = 0;

  while(high>=low){
    middle = (low+high)/2;
    *count = *count + 1;
    if(arr[middle] == key){
      result=middle;
      break;
    }
    else if(key>arr[middle])
      low = middle + 1;
    else
      high = middle - 1;
  }
  return result;
}

int main(int args, char ** argv)
{
  char* ucinetid = "NO_UCINETID";
  if (args > 1) {
    ucinetid = argv[1];
  }

  //Change intArray and keyArray to vary tests
  //Remember intArray must be sorted in ascending order with 1<=size<=100
  int intArray[] = {1,2,3,4,5,6,7,8,9,10}; 
  int keyArray[] = {2,1,4,11,13};
	
  int intArraySize = sizeof(intArray)/sizeof(int);
  int keyArraySize = sizeof(keyArray)/sizeof(int);

  int expectedCount[1];
  int theirCount[1];
  int i;
  int expectedResult=-1, theirResult = -1;

  int totalCorrect = 0;
  //printf ("Name: %s\nID#: %s\nUCINetID: %s\n", name, studentID, netID);

  /*printf("\n\nInput array:\n");
    for(i=0;i<intArraySize;i++)		
    printf("%d ",intArray[i]);

    printf("\n\nKeys:\n");
    for(i=0;i<keyArraySize;i++)	
    printf("%d ",keyArray[i]);*/
	
  //Tests
  for(i=0;i<keyArraySize;i++) {
    *expectedCount = 0;
    expectedResult =  binarySearchInC(intArray, intArraySize, keyArray[i], expectedCount);
    //printf("\n\nKey %d should be at position %d, and count should be %d\n", keyArray[i], result, *count);
    //printf("%d", result);
    *theirCount = 0;
    theirResult =  binarySearch(intArray, intArraySize, keyArray[i], theirCount);
    //printf("\nYour result: key %d is at position %d, and count equals %d\n", keyArray[i], result, *count);
    
    // score this result
    if (expectedResult == theirResult)
      totalCorrect+=resultPoints;
    
    if (*expectedCount == *theirCount)
      totalCorrect+=countPoints;
    // partial credit for off by one errors in # of checks
    else if (*expectedCount == *theirCount -1 || *expectedCount == *theirCount + 1)
      totalCorrect+=countPoints/2;
  }

  // Output results to file
  ofstream out_file;
  out_file.open(ucinetid);
  out_file << ucinetid << "," << totalCorrect << endl;
  out_file.close();

  return 0;
}

// uncomment to compile without linking to student submissions
/*int  binarySearch(int* arr, int arrSize, int key, int* count)
{
  int result=-1;
  int low =0;
  int high = arrSize-1;
  int middle;
  *count = 0;

  while(high>=low){
    middle = (low+high)/2;
    *count = *count + 1;
    if(arr[middle] == key){
      result=middle;
      break;
    }
    else if(key>arr[middle])
      low = middle + 1;
    else
      high = middle - 1;
  }
  return result;
}
*/
