import React from 'react';


export default class Home extends React.Component {
  render() {
    return (
      <div className="content-container home">
        <section className="hero">
          <div className="text-content">
            <h1>GO train late?</h1>
            <h1>Collect your <span>refund.</span>  <br/> We'll notify you.</h1>
          </div>

          <div className="button-content">
            <a href="" className="get-started">
              Get Started
            </a>
          </div>
        </section>
      </div>
      );
    }
  }
