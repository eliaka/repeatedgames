////////////////////////////////////////////////////////////////////////
//              JS-CODE FOR Repeated Games Experiment                 //
//                       AUTHOR: Elif Akata                           //
//                        MUNICH, May 2024                            //
////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////
//INTIALIZE 
////////////////////////////////////////////////////////////////////////

//data storage ref
var ntrials=10,//number of trials
    nblocks=2,//number of blocks
    trial=0,//trial counter
    block=0,//block counter
    llmVariation=0,//variation of the LLM, base or pre-prompted
    out=0,//outcome
    totalscore=0,//total score
    index=0,//index
    age=0,//age of participant
    gender=0,//gender of particpant
    handed=0,//handedness of participant
    opponent1=-1,//opponent 1
    opponent2=-1,//opponent 2
    instcounter=0,//instruction counter
    overallscore=0,//overall score
    invalidPoints = 0,  // Initialize the invalid points counter
    xcollect=[],//collecting the selected position
    ycollect=[],//collecting the returned output
    timecollect=[],//collection the timestamps
    subjectID = 0,
    studyID = 0,
    x=[],//underlying position
    y=[],//underlying outcome
    timeInMs=0,//reaction time
    letter='<input type="image" src="figs/',//the letter
    pspecs='.png"  width="120" height="120"'//size of box
    
//borders for selections
var borders=['border="1">','border="1">'];

//leter boxes and their borders
var b1=letter+'F'+pspecs+borders[0],
    b2=letter+'J'+pspecs+borders[1];

//randomly select the first block (either 0 or 1)
const firstBlock = Math.floor(Math.random() * 2);  //will be 0 or 1
const secondBlock = firstBlock === 0 ? 1 : 0;  //will be the opposite of firstBlock
const blockOrder = [firstBlock, secondBlock];  //will be an array of 0 and 1

var currentBlock = blockOrder[block];

//generating lists to collect the outcomes
for(var i=0; i<nblocks; i++) 
{
    //outcomes of arm positions
    xcollect[i] = Array.apply(null, Array(0)).map(Number.prototype.valueOf,-99);
    //outcome of y position
    ycollect[i] = Array.apply(null, Array(0)).map(Number.prototype.valueOf,-99);
    //timestamp collection
    timecollect[i] = Array.apply(null, Array(0)).map(Number.prototype.valueOf,-99);
}


////////////////////////////////////////////////////////////////////////
//CREATE HELPER FUNCTIONS
////////////////////////////////////////////////////////////////////////

//function to hide one html div and show another
function clickStart(hide, show)
{
    document.getElementById(hide).style.display ='none' ;
    document.getElementById(show).style.display ='block';
    window.scrollTo(0,0);        
}

// color text
function color(id, col) {
    document.getElementById(id).style.color = col;
}

//changes inner HTML of div with ID=x to y
function change(x,y)
{
    document.getElementById(x).innerHTML=y;
}

//Hides div with id=x
function hide(x)
{
    document.getElementById(x).style.display='none';
}

//shows div with id=x
function show(x)
{
    document.getElementById(x).style.display='block';
    window.scrollTo(0,0);
}

//creates a random number between min and max
function randomNum(min, max) {
  return Math.floor(Math.random() * (max - min + 1) + min)
}

//Display a float to a fixed percision
function toFixed(value, precision) 
{
    var precision = precision || 0,
        power = Math.pow(10, precision),
        absValue = Math.abs(Math.round(value * power)),
        result = (value < 0 ? '-' : '') + String(Math.floor(absValue / power));

    if (precision > 0) {
        var fraction = String(absValue % power),
            padding = new Array(Math.max(precision - fraction.length, 0) + 1).join('0');
        result += '.' + padding + fraction;
    }
    return result;
}

function redirect_to_prolific() {
  jatos.endStudyAndRedirect("https://app.prolific.co/submissions/complete?cc=CC")
}

////////////////////////////////////////////////////////////////////////
//Instruction Check
////////////////////////////////////////////////////////////////////////

var turkid=0;
function getprolificparameters()
{
  if (window.location.search.indexOf('PROLIFIC_PID') > -1) {
    subjectID = getQueryVariable('PROLIFIC_PID');
  }
  // If no ID is present, generate one using random numbers - this is useful for testing
  else {
    subjectID = 'test-' + Math.floor(Math.random() * (2000000 - 0 + 1)) + 0; 
  }
  // STUDY ID
  if (window.location.search.indexOf('STUDY_ID') > -1) {
    studyID = getQueryVariable('STUDY_ID');
  }
  else { 
    studyID = 'data'
  }
}

function getQueryVariable(variable)
{
    var query = window.location.search.substring(1);
    var vars = query.split("&");
    for (var i=0;i<vars.length;i++) {
        var pair = vars[i].split("=");
        if(pair[0] == variable){return pair[1];}
    }
    return(false);
}

var elem = document.documentElement;

// View in fullscreen 
function openFullscreen(start, landing) {
  getprolificparameters();
  if (elem.requestFullscreen) {
    elem.requestFullscreen();
  } else if (elem.webkitRequestFullscreen) { /* Safari */
    elem.webkitRequestFullscreen();
  } else if (elem.msRequestFullscreen) { /* IE11 */
    elem.msRequestFullscreen();
  }
  clickStart(start, landing);
}

function colorWrongAnswer(question, col){
  const rbs = document.querySelectorAll('input[name="'+question+'\"]');
  for (const rb of rbs) {
      if (rb.checked) {
          color(question+rb.id, col) 
          break;
      }
    }
}

function checkOnPage(page){
  if (document.getElementById(page).style.display == 'block'){return true}
  else {return false}
}

function changeColor(element, color){
  document.getElementById(element).style.color = color;
}

var flag = 0;
function instructioncheck() {

  //check if correct answers are provided
  if (document.getElementById('icheck1').checked) { var ch1 = 1; color('q1icheck1', 'green') } 
  else{colorWrongAnswer("q1", 'red')}
  if (document.getElementById('icheck2').checked) { var ch2 = 1; color('q2icheck2',  'green') }
  else{colorWrongAnswer("q2", 'red')}
  if (document.getElementById('icheck3').checked) { var ch3 = 1; color('q3icheck3', 'green') }
  else{colorWrongAnswer("q3", 'red')}
  if (document.getElementById('icheck4').checked) { var ch4 = 1; color('q4icheck4', 'green') }
  else{colorWrongAnswer("q4", 'red')}
  
  //are all of the correct
  var checksum = ch1 + ch2 + ch3 + ch4;

  // indicate correct answers
  clickStart('page7', 'page7');
  change("check", "Continue");

  // page transition 
  if (checksum === 4) {
    change("check", "Continue");
    //if correct, continue 
    clickStart('page7', 'page7a');
  } else { 
    instcounter++;
    //if one or more answers are wrong, raise alert box
    alert('You have answered some of the questions wrong. Please try again.');
    // go back to instructions
    clickStart('page7', 'page1');     
    }
}

function wait() {
  stopCountdown();
  document.getElementById('page7a').style.display = 'none';
  document.getElementById('page7a1').style.display = 'none';
  document.getElementById('page7b').style.display = 'block';
  // Choose a random number between 30 and 40
	let x = Math.floor(Math.random() * 11) + 30;

  // Wait for x seconds before proceeding to the next page
  setTimeout(function() {
    document.getElementById('page7b').style.display = 'none';
    document.getElementById('page8').style.display = 'block';
    begintrial();
  }, x * 1000);
}

// returns argmax of an array
function argMax(array) {
  return [].map.call(array, (x, i) => [x, i]).reduce((r, a) => (a[0] > r[0] ? a : r))[1];
}

// Function to add a new row to the table
function addHistoryRow(opponent, you, opponentScore, yourScore) {
  var table = document.getElementById('currentGameHistory');
  var newRow = table.insertRow();

  var cell1 = newRow.insertCell(0);
  var cell2 = newRow.insertCell(1);
  var cell3 = newRow.insertCell(2);
  var cell4 = newRow.insertCell(3);
  var cell5 = newRow.insertCell(4);

  cell1.innerHTML = trial + 1;
  cell2.innerHTML = opponent;
  cell3.innerHTML = opponentScore;
  cell4.innerHTML = you;
  cell5.innerHTML = yourScore;
}

// Function to clear the table (if needed)
function clearHistory() {
  var table = document.getElementById('currentGameHistory');
  while (table.rows.length > 0) {
    table.deleteRow(0);
  }
  historyVars = ["", "", "", ""];
}

function updateImage(gameNumber) {
  var imgElement = document.getElementById('dynamicImage');

  if (gameNumber === 0) {
      imgElement.src = "figs/game-1.jpg"; // New image source when condition is true
  } else {
      imgElement.src = "figs/game-2.jpg"; // Alternative image source
  }
}

////////////////////////////////////////////////////////////////////////
//Experiment
////////////////////////////////////////////////////////////////////////

var blockStatusDiv = document.getElementById("currentGameRules");
var blockStatusHist = document.getElementById("currentGameHistory");

//this function initializes a trial
function begintrial()
{
  startCountdown();
  //randomly select the LLM variation base or pre-prompted (either 0 or 1)
  llmVariation = Math.floor(Math.random() * 2);  //will be 0 or 1
  // updateImage(llmVariation);
  //only allowing for one press
  var returnpressed = 0;
  //initialize time count
  timeInMs = Date.now()
  if (currentBlock === 0) {
    blockStatusDiv.innerHTML = "<h3>Game Rules</b></h3>\
                                <h4>You are now playing <b>Game 1</b></h4>\
                                <img src='figs/game-1-short.png' alt='Game 1 Rules' style='width: 50%;'>";
  } else if (currentBlock === 1) {
    blockStatusDiv.innerHTML =  "<h3>Game Rules</b></h3>\
                                <h4>You are now playing <b>Game 2</b></h4>\
                                <img src='figs/game-2-short.png' alt='Game 2 Rules' style='width: 50%;'>";
  }
  //get the pressed key
  $(document).off('keypress').keypress(function(e) 
    {
          // Check if Enter is pressed
          if (e.which == 13 && returnpressed == 0) 
                  {
                    if(timeLeft <= 0) {
                      stopCountdown();
                      //indicate that something has been pressed          
                      returnpressed=1;
  
                      randomChoice = Math.random() < 0.5 ? 'F' : 'J'; // Assign a random letter to opponentChoice
                      randinp = randomChoice === 'F' ? 0 : 1;

                      //get the time that has passed
                      timeInMs=Date.now()-timeInMs;
                      //call the function for that position
                      if (randinp === 0) {
                        myfunc(0);
                      } else {
                        myfunc(1);
                      }
                    }
                  }
          //if key equals F       
          if(e.which == 102 & returnpressed == 0)  
                  { 
                    if(timeLeft > 0) {
                      stopCountdown();
                      //indicate that something has been pressed          
                      returnpressed=1;
                      //get the time that has passed
                      timeInMs=Date.now()-timeInMs;
                      //call the function for that position
                      myfunc(0);
                    }
                  }
          //same spiel if key equals J
          if(e.which == 106 & returnpressed == 0)  
                  {
                    if(timeLeft > 0) {
                      stopCountdown();
                      returnpressed=1;
                      timeInMs=Date.now()-timeInMs;
                      myfunc(1);
                    }
                  }
            }

          
      );
      
}

//function to draw the letter boxes into the HTML
function drawletters()
{
  change('arm1', b1);
  change('arm2', b2);
}

//do this once at start
drawletters();

let opponentLookup_bos_base = {};

fetch('lookups/bos_gpt4_lookup.json')
  .then(response => response.json())
  .then(data => opponentLookup_bos_base = data);

let opponentLookup_bos_variation = {};

fetch('lookups/bos_variation_predict_gpt4_lookup.json')
  .then(response => response.json())
  .then(data => opponentLookup_bos_variation = data);

let opponentLookup_pd_base = {};

fetch('lookups/pd_gpt4_lookup.json')
  .then(response => response.json())
  .then(data => opponentLookup_pd_base = data);
  
let opponentLookup_pd_variation = {};
  
  fetch('lookups/pd_variation_predict_gpt4_lookup.json')
    .then(response => response.json())
    .then(data => opponentLookup_pd_variation = data);

function calculate_points_bos(playerChoice, opponentChoice) {
  let playerPoints = 0;
  let opponentPoints = 0;
  // Logic to calculate points
  if (playerChoice === 1 && opponentChoice === "J") {
    playerPoints = 7;
    opponentPoints = 10;
  }
  if (playerChoice === 0 && opponentChoice === "F") {
    playerPoints = 10;
    opponentPoints = 7;
  }
  if (playerChoice === 1 && opponentChoice === "F") {
    playerPoints = 0;
    opponentPoints = 0;
  }
  if (playerChoice === 0 && opponentChoice === "J") {
    playerPoints = 0;
    opponentPoints = 0;
  }
  return { playerPoints, opponentPoints };
}

function calculate_points_pd(playerChoice, opponentChoice) {
  let playerPoints = 0;
  let opponentPoints = 0;
  // Logic to calculate points
  if (playerChoice === 1 && opponentChoice === "J") {
    playerPoints = 8;
    opponentPoints = 8;
  }
  if (playerChoice === 0 && opponentChoice === "F") {
    playerPoints = 5;
    opponentPoints = 5;
  }
  if (playerChoice === 1 && opponentChoice === "F") {
    playerPoints = 0;
    opponentPoints = 10;
  }
  if (playerChoice === 0 && opponentChoice === "J") {
    playerPoints = 10;
    opponentPoints = 0;
  }
  return { playerPoints, opponentPoints };
}

function startCountdown() {
  // Clear existing countdown interval if it exists
  if (countdown) {
    clearInterval(countdown);
  }

  timeLeft = 20;  // Reset the countdown timer
  countdown = setInterval(() => {
    if (timeLeft <= 0) {
      clearInterval(countdown);
      countdown = null; // Ensure the countdown variable is cleared after stopping the interval
      change('outcome', "");
      countdownElement.innerHTML = "Time's up! You will be asigned a random option and won't earn monetary reward for this round.<br><br>Press <b>Enter</b> to continue.";
      document.getElementById('continueButton').style.display = 'block'; // Show the button
    } else {
      countdownElement.textContent = timeLeft + " seconds remaining...";
    }
    timeLeft -= 1;
  }, 1000);
}

function stopCountdown() {
  clearInterval(countdown);
  countdownElement.textContent = ""; // Clear the 'countdown' HTML element
}

let countdownElement = document.getElementById('countdown');
let countdown;

let playerChoices = "";  // Initialize an empty string to store player choices
let historyMessage = "";  // Initialize an empty string to store the history of the game
let historyVars = ["", "", "", ""];  // Initialize an empty string to store the history of the game

// Function that executes the bandit
function myfunc(inp) {
  // Initialize the opponent's choice
  let opponentChoice;

  if (currentBlock === 0) {
    // Lookup opponent's choice based on player's past choices
    if (llmVariation === 0) {
      opponentChoice = opponentLookup_bos_base[playerChoices];
    } else if (llmVariation === 1) {
      opponentChoice = opponentLookup_bos_variation[playerChoices];
    }
  } else if (currentBlock === 1) {
    // Lookup opponent's choice based on player's past choices
    if (llmVariation === 0) {
      opponentChoice = opponentLookup_pd_base[playerChoices];
    } else if (llmVariation === 1) {
      opponentChoice = opponentLookup_pd_variation[playerChoices];
    }
  }

  // Append the player's choice to the running record
  playerChoices += inp === 0 ? "F" : "J";

  // Calculate points for both the player and opponent
  // let { playerPoints, opponentPoints } = calculate_points_bos(inp, opponentChoice);
  // Choose which calculatePoints function to use based on the current block
  let playerPoints, opponentPoints;
  if (currentBlock === 0) {
    ({ playerPoints, opponentPoints } = calculate_points_bos(inp, opponentChoice));
  } else if (currentBlock === 1) {
    ({ playerPoints, opponentPoints } = calculate_points_pd(inp, opponentChoice));
  }

  out=playerPoints;
  
  // Collect the chosen location
  xcollect[block][trial] = inp; 
  // Collect returned value
  ycollect[block][trial] = out;
  // Collect reaction time
  timecollect[block][trial] = timeInMs;

  // Mark the selected option
  borders[inp] = 'border="4">';
  // Update letter boxes
  let b1 = letter + 'F' + pspecs + borders[0];
  let b2 = letter + 'J' + pspecs + borders[1];
  // Draw the options with their letters; now the chosen one has a thicker frame
  drawletters();

  let outcomeMessage;
  if(timeLeft <= 0) {
      invalidPoints += playerPoints;
      if (trial === 9) {
        outcomeMessage = `
          In round ${trial+1}, you didn't make a choice so you're assigned the random choice ${inp === 0 ? "F" : "J"}.<br><br>
          This was the last round of this game. Please wait...<br>
          <img src="figs/three-dots.webp" alt="waiting" style="width: 100px; height: auto;">
        `;
        historyMessage = `
          <span style="color: #0000FF;">You were assigned ${inp === 0 ? "F" : "J"}</span> and won <span style="color: #0000FF;">${playerPoints} invalid points</span><br>
          <span style="color: #ff0000;">Other player chose ${opponentChoice}</span> and won <span style="color: #ff0000;">${opponentPoints} points</span><br><br>
          This was the last round of this game. Please wait...<br>
          <img src="figs/three-dots.webp" alt="waiting" style="width: 100px; height: auto;">
        `;
      } else {
        outcomeMessage = `
          In round ${trial+1}, you didn't make a choice so you're assigned the random choice ${inp === 0 ? "F" : "J"}.<br><br>
          Round ${trial+2} will start soon. Please wait...<br>
          <img src="figs/three-dots.webp" alt="waiting" style="width: 100px; height: auto;">
        `;
        historyMessage = `
          <span style="color: #0000FF;">You were assigned ${inp === 0 ? "F" : "J"}</span> and won <span style="color: #0000FF;">${playerPoints} invalid points</span><br>
          <span style="color: #ff0000;">Other player chose ${opponentChoice}</span> and won <span style="color: #ff0000;">${opponentPoints} points</span><br><br>
          Round ${trial+2} will start soon. Please wait...<br>
          <img src="figs/three-dots.webp" alt="waiting" style="width: 100px; height: auto;">
        `;
      }
  } else {
      if (trial === 9) {
        outcomeMessage = `
          <span style="color: #0000FF;">You chose ${inp === 0 ? "F" : "J"}</span><br><br>
          This was the last round of this game. Please wait...<br>
          <img src="figs/three-dots.webp" alt="waiting" style="width: 100px; height: auto;">
        `;
        historyMessage = `
          <span style="color: #0000FF;">You chose ${inp === 0 ? "F" : "J"}</span> and won <span style="color: #0000FF;">${playerPoints} points</span><br>
          <span style="color: #ff0000;">Other player chose ${opponentChoice}</span> and won <span style="color: #ff0000;">${opponentPoints} points</span><br><br>
          This was the last round of this game. Please wait...<br>
          <img src="figs/three-dots.webp" alt="waiting" style="width: 100px; height: auto;">
        `;
      } else {
        outcomeMessage = `
          <span style="color: #0000FF;">You chose ${inp === 0 ? "F" : "J"}</span><br><br>
          Round ${trial+2} will start soon. Please wait...<br>
          <img src="figs/three-dots.webp" alt="waiting" style="width: 100px; height: auto;">
        `;
        historyMessage = `
          <span style="color: #0000FF;">You chose ${inp === 0 ? "F" : "J"}</span> and won <span style="color: #0000FF;">${playerPoints} points</span><br>
          <span style="color: #ff0000;">Other player chose ${opponentChoice}</span> and won <span style="color: #ff0000;">${opponentPoints} points</span><br><br>
          Round ${trial+2} will start soon. Please wait...<br>
          <img src="figs/three-dots.webp" alt="waiting" style="width: 100px; height: auto;">
        `;
      }
  }

  // Display on screen
  change('outcome', outcomeMessage);
  historyVars = [opponentChoice, inp === 0 ? "F" : "J", opponentPoints, playerPoints];

  setTimeout(function() {
    change('outcome', historyMessage);
  }, Math.random() * (10000 - 5000) + 5000);

  // Set a timeout; after 2 seconds, start the next trial
  setTimeout(function() {
    nexttrial();
  }, Math.max(15000, 25000 - timeInMs));

}

function nexttrial()
{
  // // change('currentGameHistory', historyMessage);
  addHistoryRow(historyVars[0], historyVars[1], historyVars[2], historyVars[3]);

  //check if trials are smaller than the maximum trial number
  if (trial+1<ntrials)
  {
    //set the borders back to normal
    borders=['border="1">','border="1">'];
    //change the letters again
    b1=letter+'F'+pspecs+borders[0];
    b2=letter+'J'+pspecs+borders[1];
    //draw options and their letters
    drawletters();
    //begin new trial
    begintrial();
    //track total score
    totalscore += out;
    overallscore += out;
    //to be inserted total score
    var inserts='Total Score: '+toFixed(totalscore,0);
    //show total score on screen
    // change('score', inserts);
    //increment trial number
    trial++;
    //to be inserted number of trials left
    var insertt='Rounds left: '+(ntrials-trial-1);
    //show on screen
    change('remain', insertt);
    //change ooutcome back to please choose an option
    change('outcome', "Please choose an option!");  
  }
  //if trial numbers exceed the total number, check if more blocks are available
  else if (trial+1==ntrials & block+1<nblocks)
  {
    //tell them that this block is over
    // alert("Game " +(block+1)+" out of 2 is over. Please press Enter to continue with the next game.")

    document.getElementById('page8').style.display = 'none'; // hide page8
    document.getElementById('page7a1').style.display = 'block'; // display page7a immediately
    //start next block
    nextblock();
  }else
  {
    //Otherwise --if blocks exceed total block number, then the experiment is over
    // alert("The experiment is over. You will now be directed to the next page.")
    clickStart('page8', 'page9');
  }
}

//function to initialize next block
function nextblock()
{
  playerChoices = "";
  historyMessage = "";
  // change('currentGameHistory', historyMessage);
  clearHistory();
  borders=['border="1">','border="1">'];
  //new letters and boxes
  b1=letter+'F'+pspecs+borders[0];
  b2=letter+'J'+pspecs+borders[1];
  //draw options
  drawletters();
  //increment block number
  block++;
  //get random block
  currentBlock = blockOrder[block];
  //begin a new trial
  begintrial();
  //set trial number back to 0
  trial=0;
  //total score back to 0
  totalscore=0;
  //insert total score
  var inserts='Total Score: '+toFixed(totalscore,0);
  var insertt='Number of trials left: '+(ntrials-trial);
  //on screen
  change('remain', insertt);
  //ask them to choose an outcome
  change('outcome', "Please choose an option!");
}

////////////////////////////////////////////////////////////////////////
//Demographics & Finish
////////////////////////////////////////////////////////////////////////

//sets the selected gender
function setgender(x)
{
  gender=x;
  return(gender)
}

//sets the selected age
function setage(x)
{
  age=x;
  return(age)
}

//sets the selected handedness
function sethanded(x)
{
  handed=x;
  return(handed)
}

function setopponent1(x)
{
  opponent1=x;
  return(opponent1)
}

function setopponent2(x)
{
  opponent2=x;
  return(opponent2)
}

//data to save string to downloads
function saveText(text, filename){
  //creat document
  var a = document.createElement('a');
  //set ref
  a.setAttribute('href', 'data:text/plain;charset=utf-u,'+encodeURIComponent(text));
  //to download
  a.setAttribute('download', filename);
  //submit
  a.click()
}

function saveData(filedata){
  var filename = "./data/" + subjectID + ".json";  
  $.post("save_data.php", {postresult: filedata + "\n", postfile: filename })
}

function mysubmit()
{
  var PROLIFIC_PID = jatos.urlQueryParameters.PROLIFIC_PID;
  //change page
  clickStart('page9a','page9b');
  //claculate score
  let flattenedRewards = ycollect.flat();
  let totalRewards = flattenedRewards.reduce((acc, current) => acc + current, 0);
  var presenttotal = 'You have gained a total score of ' + totalRewards + ' with ' + (totalRewards-invalidPoints) + ' valid points.';
  //calculate money earned
  var money = 3 + ((totalRewards-invalidPoints)*0.01);
  money = Math.max(toFixed(money, 2), 3);
  var bonus = (totalRewards-invalidPoints)*0.01;
  bonus = toFixed(bonus, 2);
  var presentmoney = 'This equals a total reward of £' + money;
  //show score and money
  change('result',presenttotal); 
  change('money',presentmoney);
  //all data to save
  saveDataArray = {
    'actions': xcollect,
    'rewards': ycollect,
    'firstGame': firstBlock,
    'secondGame': secondBlock,
    'llmVariation': llmVariation,
    'times': timecollect,
    'invalidPoints': invalidPoints,
    'totalScore': totalRewards,
    'money': money,
    'bonus': bonus,
    'opponent1': opponent1,
    'opponent2': opponent2,
    'age': age,
    'gender': gender,
    'instcounter': instcounter,
    'prolificID': PROLIFIC_PID,
  };
  //save data
  jatos.submitResultData(saveDataArray);
}

////////////////////////////////////////////////////////////////////////
//The END
////////////////////////////////////////////////////////////////////////