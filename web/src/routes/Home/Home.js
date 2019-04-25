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

          <div className="link-content">
            <a href="">How it works</a>
          </div>
        </section>

        <section className="links row">
          <a href="">
            <i className="fas fa-train"></i>
            <h4>Check GO Trip Status</h4>
          </a>

          <a href="">
            <i className="fas fa-hand-holding-usd"></i>
            <h4>View Eligible Refunds</h4>
          </a>
        </section>

        <section className="how-it-works">
          <h2 className="title">How it works</h2>

          <div className="sub-section">
            <h3 className="title left">one</h3>

            <div className="text-content left">
              Sign in (with your Google account).
            </div>
          </div>

          <div className="sub-section">
            <h3 className="title right">one</h3>

            <div className="text-content right">
              Sign in (with your Google account).
            </div>
          </div>
        </section>
      </div>
      );
    }
  }
