# Place

Place is a recurring collaborative project and social experiment on the Reddit platform where users edit a shared pixel canvas together.

The project is a huge canvas on which participants place pixels, creating collective art, flags, memes and other images. The project implies a heavy CCU load - tens of thousands of reads per second and thousands of writes per second (in 2022, 10.5 million users with 160 million changes)

## How r/place works: Rules and features provided

The main idea is to create pixel art together with constraints to encourage coordination and creativity. Here are the key aspects:

- [x] **Canvas**: `canvas` 1000x1000 pixels (1 million squares), color palette - 32.
  - [ ] Customizable canvas size - choosing the size suitable for `tile`
- [ ] **Registration and Access**: Participation requires OAuth 2.0 authorization. Users can change the color of one pixel on the canvas from the color palette. After placing a pixel, a timer is triggered (customizable).
- [ ] **Moderation and Completion**: Administrators can place an unlimited number of pixels to remove inappropriate content. In the final hours of the events, the placement was limited to a palette of only white and gray colors, which led to a gradual "bleaching" of the canvas.
- [ ] **Additional Features**: The open API allows the community to create bots, extensions, data collection and visualization tools. Peak activity is millions of pixels per hour, with high engagement.
- [ ] **Time-lapse generation**: Generate videos based on user activity
