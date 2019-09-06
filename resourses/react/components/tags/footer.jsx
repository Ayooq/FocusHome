import React from 'react';
import {Link} from 'react-router-dom';

class Footer extends React.Component{
  constructor(props) {
    super(props);
  }



  render(){
    return <footer className="bdT ta-c p-30 lh-0 fsz-sm c-grey-600">
      <span>Copyright © 2019 <a href="#" target="_blank" title="Colorlib">FOCUS</a>. All rights reserved.</span>
    </footer>
  }
}

Footer.defaultProps = {

};

export default Footer;