#include <stdio.h>
#define PI 3.1416

/*
Computes the volume and surface area of a cylinder.
Reads the user input on the radius and height of the cylinder, and then computes the volume and surface area of the cylinder.
*/

int main()
{
    float radius, height;

    printf("Enter the radius: ");
    scanf("%f", &radius);
    printf("Enter the height: ");
    scanf("%f", &height);

    float volume = PI * radius * radius * height;
    float area = 2 * PI * ((radius * height) + (radius * radius));

    printf("The volume is: %.2f\n", volume);
    printf("The surface area is: %.2f", area);

    return 0;
}
