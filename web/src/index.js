import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter as Router, Route, Link } from "react-router-dom";

import Home from './routes/Home/Home';
import Contact from './routes/Contact/Contact';


class App extends React.Component {
  render() {
    return (
      <Router>
        <nav className="row site-header">
          <h3 className="col site-title">GO Refund App</h3>
          <div className="col sign-in">
            {/* <button className="unstyled"><i className="fab fa-google"></i> <span>Sign in</span></button> */}
            <div className="g-signin2" data-onsuccess="onSignIn"></div>
          </div>
        </nav>
        <div>
          <Route path="/" exact component={Home} />
          <Route path="/contact/" component={Contact} />
        </div>
      </Router>
    );
  }
}


ReactDOM.render(<App />, document.getElementById("app"));

function onSignIn(googleUser) {
  var profile = googleUser.getBasicProfile();
  console.log('ID: ' + profile.getId()); // Do not send to your backend! Use an ID token instead.
  console.log('Name: ' + profile.getName());
  console.log('Image URL: ' + profile.getImageUrl());
  console.log('Email: ' + profile.getEmail()); // This is null if the 'email' scope is not present.
}
window.onSignIn = onSignIn;
