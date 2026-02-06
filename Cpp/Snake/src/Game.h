#pragma once
#include "Snake.h"
#include "raylib.h"
#include <string>

enum class GameState {
    MENU,
    PLAYING,
    GAME_OVER
};

enum class Difficulty {
    EASY,
    MEDIUM,
    HARD
};

class Game {
public:
    Game();
    ~Game();
    void Run();

private:
    void Init();
    void Update();
    void Draw();
    void HandleInput();
    void SpawnFood();
    void CheckCollision();
    void DrawMenu();
    void DrawGameOver();

    Snake snake;
    Point food;
    int score;
    GameState state;
    Difficulty difficulty;
    
    // Grid settings
    const int cellSize = 30;
    const int cellCount = 20; // 20x20 grid = 600x600 window
    const int offset = 75;    // Top offset for score/UI
    
    double lastUpdateTime;
    double updateInterval;
    
    bool EventTriggered(double interval);
};
