const express = require('express')
const app = express()
const port = 3000

//TODO add user functionality

app.get('/', (req, res) => {
  res.send('This is an Expense Tracker Application!')
})

app.post('/addexpense', (req, res) => {
  
})