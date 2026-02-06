#include "Snake.h"
#include <deque>

Snake::Snake() {
    Reset();
}

void Snake::Reset() {
    body = {
        {6, 9},
        {5, 9},
        {4, 9}
    };
    direction = {1, 0};
    addSegment = false;
    color = { 173, 204, 96, 255 }; // Greenish color
}

void Snake::Draw() {
    for (unsigned int i = 0; i < body.size(); i++) {
        float x = (float)body[i].x;
        float y = (float)body[i].y;
        Rectangle segment = { x * 30 + 75, y * 30 + 75, 30, 30 }; // +75 for offset (padding + top UI)
        // Adjust logic later if offset logic changes in Game.cpp
        
        // Actually, let's keep it simple and assume the caller handles offset or we pass it in. 
        // For now, hardcoding offset 75 based on Game.h
        DrawRectangleRec(segment, color);
    }
}

void Snake::Update() {
    body.push_front({body[0].x + direction.x, body[0].y + direction.y});
    if (addSegment) {
        addSegment = false;
    } else {
        body.pop_back();
    }
}

void Snake::Grow() {
    addSegment = true;
}
