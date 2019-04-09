import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter as Router, Route, Link } from "react-router-dom";

import Home from './routes/Home/Home';
import Contact from './routes/Contact/Contact';


class App extends React.Component {
  render() {
    return (
      <Router>
        <div>
          <Route path="/" exact component={Home} />
          <Route path="/contact/" component={Contact} />
        </div>
      </Router>
    );
  }
}


ReactDOM.render(<App />, document.getElementById("app"));
