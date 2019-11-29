'use strict';
 
 // This file contains the code running in the Google Dialogflow Fulfillment
 // It defines the communication flow between Google Assistant and the assisted person,
 // asking whether the person needs help and calling the Telegram notification service if help is required. 

const requestNode = require('request');
const {dialogflow} = require('actions-on-google');
const functions = require('firebase-functions');
const rp = require("request-promise-native");

//Definition of the Intents
const HELP_INTENT = 'I cannot find nemo - not okay';
const No_ANSWER_INTENT = 'Reprompt';
const No_NEMO = 'I cannot find nemo';
const FallBackHelpQuestion = 'FallBackHelpQuestion';
const FollowUpContext =  'Icantfindnemo-followup'; 


const url = 'http://<webServiceIP>:54321/notificationRequest';
const data ={
  'chat_id':'<chatId>',
  'text':'Hey, it seems nemo needs help. Please look after him!'
};

const app = dialogflow({debug: true});

//Dialogflow Intents
app.intent(No_NEMO, (conv) => {
  conv.data.fallbackCount = 0;
  conv.ask("Hey nemo, are you okay?");
});

app.intent(HELP_INTENT, (conv) => {
  callApi2();
  conv.close("Ok. I will call help");
});

app.intent(No_ANSWER_INTENT, (conv) => {
  const repromptCount = parseInt(conv.arguments.get('REPROMPT_COUNT'));
  if (repromptCount === 0) {
    conv.ask(`Are you there? Please answer me if you are okay or need help!`);
  } else if (repromptCount === 1) {
    conv.ask(`Hey nemo, I still haven't received any answer. Are you okay?`);
  } else if (conv.arguments.get('IS_FINAL_REPROMPT')) {
    callApi2();
    conv.close(`I will contact someone.`);
  }
});

app.intent(FallBackHelpQuestion, (conv) => {
 conv.data.fallbackCount++;
 // Provide two prompts before ending game
 if (conv.data.fallbackCount === 1) {
   conv.contexts.set(FollowUpContext, 5);
   conv.ask('Sorry I didn\'t get that. Are you okay?');
 }
 else if (conv.data.fallbackCount === 2) {
   conv.contexts.set(FollowUpContext, 5);
   conv.ask('I still didn\'t get that. Are you okay? Otherwise I will call help now');
 }
 else {
  callApi2();
  conv.close(`Since I'm still not understanding you, I will call help.`);
 }
});
  
exports.dialogflowFirebaseFulfillment = functions.https.onRequest(app);

// This API can be used to directly send a message to the Telegram Bot API
function callApi(){
  var options = {
      method: 'POST',
      uri: 'https://api.telegram.org/bot<token>/sendMessage',
      body: data,
      json: true // Automatically stringifies the body to JSON
  };
  rp(options)
      .then(function (parsedBody) {
      })
      .catch(function (err) {
          console.log(err);
      });
}

function callApi2(){
  var options = {
      method: 'GET'

  };
  rp(options)
      .then(function (parsedBody) {
      })
      .catch(function (err) {
          console.log(err);
      });
}
