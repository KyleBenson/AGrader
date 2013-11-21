#include<stdio.h>

#ifndef _list
#define _list
typedef struct linked_list {
  struct linked_list *next_element;	 // the pointer to the next element in the list
  int value;                         // the value of the element
} list;
#endif

extern char *yourName;
extern char *studentID;
extern list* process_list(list* list_beg, list* new_element);

void main()
{
	list first, second, third, fourth, fifth, sixth, newElem; ///// we define some elements
	list *list_ptr, *p,*q; // we define a pointer to an element or a list, 
	 	               // the pointer initially points to a dummy location.

	first.value=3;                    /////////// intialization.
	first.next_element=&second;        /////////// the pointer of the second obejct is copied to the first.next_element.

	second.value=5;
	second.next_element=&third;

	third.value=5;
	third.next_element=&fourth;

	fourth.value=3;
	fourth.next_element=&fifth;

	fifth.value=0;
	fifth.next_element=&sixth;       

	sixth.value=2;
	sixth.next_element=NULL;		////////////  NULL is defined in <stdio.h>
	
	newElem.value = 7;
	newElem.next_element =NULL;
	list_ptr=&first;
	printf("Name: %s\nID: %s\n", yourName,studentID);
	//************************test1
	printf("\nTest1, the linked list is\n");
	p = list_ptr;
	while(p!=NULL){
		printf("\t%d",p->value);
		p= p->next_element;
	}
	printf("\nyou need to delete the maximum element and insert %d after element 0",newElem.value);
	p = list_ptr;
	q=process_list(p,&newElem);
	p = list_ptr;
	printf("\nThe result should be \t3\t3\t0\t7\t2\nReturn the pointer to element 0\nYour result is\t");
	while(p!=NULL){
		printf("\t%d",p->value);
		p= p->next_element;
	}
	if(q!=NULL)
		printf("\nReturn the pointer to element %d\n", q->value);
	else
		printf("\nReturn element NULL\n");
	
	//***********************test2
	printf("\nTest2, the linked list is NULL");	
	printf("\nyou need to delete the maximum element and insert %d after element 0",newElem.value);
	p = NULL;
	q = process_list(p,&newElem);

	printf("\nThe result should return the pointer to element NULL");

	if(q==NULL) 
		printf("\nYour result returns the pointer to element NULL");
	else
		printf("\nYour result returns the pointer to element %d", q->value);
	printf("\n");

//	*****************************test3
	newElem.value = 100;
	newElem.next_element =NULL;
	first.next_element = &fourth;
	fourth.value = 4;
	fourth.next_element = NULL;

	printf("\nTest3, the linked list is\n");
	p = list_ptr;
	while(p!=NULL){
		printf("\t%d",p->value);
		p= p->next_element;
	}
	printf("\nyou need to delete the maximum element and insert %d after element 0",newElem.value);
	p = list_ptr;
	q=process_list(p,&newElem);
	p = list_ptr;
	printf("\nThe result should be \t3\nReturn the pointer to element NULL\nYour result is\t");
	while(p!=NULL){
		printf("\t%d",p->value);
		p= p->next_element;
	}
	if(q!=NULL)
		printf("\nReturn the pointer to element %d\n", q->value);
	else
		printf("\nReturn pointer to element NULL\n");


	//	*****************************test4
	newElem.value = 100;
	newElem.next_element =NULL;
	first.value = 10;
	first.next_element = &second;
	second.value = 12;
	second.next_element = &third;
	third.value = 0;
	third.next_element = NULL;
	printf("\nTest4, the linked list is\n");
	p = list_ptr;
	while(p!=NULL){
		printf("\t%d",p->value);
		p= p->next_element;
	}
	printf("\nyou need to delete the maximum element and insert %d after element 0",newElem.value);
	p = list_ptr;
	q=process_list(p,&newElem);
	p = list_ptr;
	printf("\nThe result should be \t10\t0\t100\nReturn the pointer to element 0\nYour result is\t");
	while(p!=NULL){
		printf("\t%d",p->value);
		p= p->next_element;
	}
	if(q!=NULL)
		printf("\nReturn the pointer to element %d\n", q->value);
	else
		printf("\nReturn element NULL\n");
}
