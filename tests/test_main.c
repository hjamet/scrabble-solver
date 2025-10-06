#include "engine.h"
#include <stdio.h>

int main(void) {
    printf("Testing Scrabble Engine...\n");
    
    /* Test engine initialization */
    if (engine_init() != 0) {
        printf("ERROR: Engine initialization failed\n");
        return 1;
    }
    printf("✓ Engine initialization successful\n");
    
    /* Test engine cleanup */
    engine_cleanup();
    printf("✓ Engine cleanup successful\n");
    
    printf("All tests passed!\n");
    return 0;
}
