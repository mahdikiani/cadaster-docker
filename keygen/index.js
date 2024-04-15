// import express from express;
const express = require('express');
const rTile = require('./sec');
// import { rTile } from "./sec";

const app = express();

// Define a route for handling GET requests
app.get('/key', (req, res) => {
    // Get the three arguments from the query parameters
    const { x, y, z } = req.query;

    // Check if all three arguments are provided
    if (!x || !y || !z) {
        return res.status(400).send('Please provide three arguments. x, y, z');
    }

    // Parse the arguments as numbers
    const X = parseFloat(x);
    const Y = parseFloat(y);
    const Z = parseFloat(z);

    // Check if any argument is not a valid number
    if (isNaN(X) || isNaN(Y) || isNaN(Z)) {
        return res.status(400).send('Please provide valid numbers.');
    }

    // Calculate the sum
    const key = rTile(X, Y, Z);

    // Send the sum as the response
    res.send(`${key}`);
});

// Start the server
app.listen(3000, () => {
    console.log('Server is listening on port 3000');
});