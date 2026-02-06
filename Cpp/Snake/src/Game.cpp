#include "Game.h"
#include <random>
#include <iostream>

Game::Game() : state(GameState::MENU), score(0), updateInterval(0.2) {
    Init();
}

Game::~Game() {
    CloseWindow();
}

void Game::Init() {
    InitWindow(2 * offset + cellSize * cellCount, 2 * offset + cellSize * cellCount, "Retro Snake C++");
    SetTargetFPS(60);
    SpawnFood();
}

void Game::Run() {
    while (!WindowShouldClose()) {
        Update();
        Draw();
    }
}

void Game::Update() {
    if (state == GameState::MENU) {
        if (IsKeyPressed(KEY_ONE)) { difficulty = Difficulty::EASY; updateInterval = 0.2; state = GameState::PLAYING; }
        if (IsKeyPressed(KEY_TWO)) { difficulty = Difficulty::MEDIUM; updateInterval = 0.15; state = GameState::PLAYING; }
        if (IsKeyPressed(KEY_THREE)) { difficulty = Difficulty::HARD; updateInterval = 0.1; state = GameState::PLAYING; }
    } 
    else if (state == GameState::PLAYING) {
        HandleInput();
        if (EventTriggered(updateInterval)) {
            snake.Update();
            CheckCollision();
        }
    }
    else if (state == GameState::GAME_OVER) {
        if (IsKeyPressed(KEY_ENTER)) {
            snake.Reset();
            score = 0;
            state = GameState::MENU;
            SpawnFood();
        }
    }
}

void Game::HandleInput() {
    if (IsKeyPressed(KEY_UP) && snake.direction.y != 1) {
        snake.direction = {0, -1};
    }
    if (IsKeyPressed(KEY_DOWN) && snake.direction.y != -1) {
        snake.direction = {0, 1};
    }
    if (IsKeyPressed(KEY_LEFT) && snake.direction.x != 1) {
        snake.direction = {-1, 0};
    }
    if (IsKeyPressed(KEY_RIGHT) && snake.direction.x != -1) {
        snake.direction = {1, 0};
    }
}

void Game::SpawnFood() {
    // Generate random position
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> distr(0, cellCount - 1);
    
    while(true) {
        int x = distr(gen);
        int y = distr(gen);
        food = {x, y};
        
        // Ensure food doesn't spawn on snake body
        bool onBody = false;
        for (const auto& part : snake.body) {
            if (part == food) {
                onBody = true;
                break;
            }
        }
        if (!onBody) break;
    }
}

void Game::CheckCollision() {
    // Wall collision
    if (snake.body[0].x < 0 || snake.body[0].x >= cellCount || 
        snake.body[0].y < 0 || snake.body[0].y >= cellCount) {
        state = GameState::GAME_OVER;
    }

    // Self collision
    for (size_t i = 1; i < snake.body.size(); i++) {
        if (snake.body[0] == snake.body[i]) {
            state = GameState::GAME_OVER;
        }
    }
    
    // Food collision
    if (snake.body[0] == food) {
        score++;
        snake.Grow();
        SpawnFood();
    }
}

void Game::Draw() {
    BeginDrawing();
    ClearBackground({43, 51, 24, 255}); // Retro LCD style background

    if (state == GameState::MENU) {
        DrawText("SNAKE GAME", offset + 140, offset + 100, 40, DARKGREEN);
        DrawText("Select Difficulty:", offset + 160, offset + 200, 20, DARKGRAY);
        DrawText("1. Easy", offset + 250, offset + 240, 20, BLACK);
        DrawText("2. Medium", offset + 250, offset + 270, 20, BLACK);
        DrawText("3. Hard", offset + 250, offset + 300, 20, BLACK);
    }
    else if (state == GameState::PLAYING) {
        // Draw Border
        DrawRectangleLinesEx({(float)offset-5, (float)offset-5, (float)cellCount*cellSize+10, (float)cellCount*cellSize+10}, 5, DARKGREEN);

        // Draw Food
        DrawRectangle(offset + food.x * cellSize, offset + food.y * cellSize, cellSize, cellSize, RED);

        // Draw Snake (Handling offset manually here to match Snake.cpp assumption or fixing Snake.cpp)
        // Let's pass offset to snake or handle it here? 
        // Snake.cpp has hardcoded 75 which is our offset. That works.
        snake.Draw();

        DrawText(TextFormat("Score: %i", score), offset, 20, 40, DARKGREEN);
        DrawText("Retro Snake", offset + 400, 20, 40, DARKGREEN);
    }
    else if (state == GameState::GAME_OVER) {
        DrawText("GAME OVER", offset + 160, offset + 150, 40, RED);
        DrawText(TextFormat("Final Score: %i", score), offset + 180, offset + 220, 30, DARKGREEN);
        DrawText("Press ENTER to Play Again", offset + 130, offset + 300, 20, BLACK);
    }
    
    EndDrawing();
}

bool Game::EventTriggered(double interval) {
    double currentTime = GetTime();
    if (currentTime - lastUpdateTime >= interval) {
        lastUpdateTime = currentTime;
        return true;
    }
    return false;
}
