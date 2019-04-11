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
            <button className="unstyled"><i class="fab fa-google"></i> <span>Sign in</span></button>
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
