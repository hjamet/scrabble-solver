#ifndef ENGINE_H
#define ENGINE_H

/**
 * Initialize the Scrabble engine
 * @return 0 on success, non-zero on error
 */
int engine_init(void);

/**
 * Cleanup the Scrabble engine
 */
void engine_cleanup(void);

#endif /* ENGINE_H */
