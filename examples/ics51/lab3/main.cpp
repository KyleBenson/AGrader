#include <stdio.h>
#include <stdlib.h>

extern char* name;
extern char* studentID;
extern char* netID;
extern int binarySearch();

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

int main()
{
	//Change intArray and keyArray to vary tests
	//Remember intArray must be sorted in ascending order with 1<=size<=100
	int intArray[] = {1,2,3,4,5,6,7,8,9,10}; 
	int keyArray[] = {2,1,4,11,13};
	
	int intArraySize = sizeof(intArray)/sizeof(int);
	int keyArraySize = sizeof(keyArray)/sizeof(int);

	int count[1];
	int i, result;

	printf ("Name: %s\nID#: %s\nUCINetID: %s\n", name, studentID, netID);

	printf("\n\nInput array:\n");
	for(i=0;i<intArraySize;i++)		
		printf("%d ",intArray[i]);

	printf("\n\nKeys:\n");
	for(i=0;i<keyArraySize;i++)	
		printf("%d ",keyArray[i]);
	
	//Tests
	for(i=0;i<keyArraySize;i++) {
		*count = 0;
		result =  binarySearchInC(intArray, intArraySize, keyArray[i], count);
		printf("\n\nKey %d should be at position %d, and count should be %d\n", keyArray[i], result, *count);
		*count = 0;
		result =  binarySearch(intArray, intArraySize, keyArray[i], count);
		printf("\nYour result: key %d is at position %d, and count equals %d\n", keyArray[i], result, *count);
	}
}