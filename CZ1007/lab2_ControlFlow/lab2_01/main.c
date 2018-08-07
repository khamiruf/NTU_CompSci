#include <stdio.h>
int main()
{
    int studentNumber, mark;
    char grade;

    printf("Enter Student ID: \n");
    scanf("%d", &studentNumber);

    while (studentNumber != -1) {
        printf("Enter Mark: \n");
        scanf("%d", &mark);

        if (mark >= 75)
            grade = 'A';
        else if (mark >= 65)
            grade = 'B';
        else if (mark >= 55)
            grade = 'C';
        else if (mark >= 45)
            grade = 'D';
        else
            grade = 'F';

        printf("Grade = %c\n", grade);
        printf("Enter Student ID: \n");
        scanf("%d", &studentNumber);
    }

    return 0;
}
