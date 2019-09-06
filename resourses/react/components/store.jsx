import { createStore, combineReducers } from 'redux';
import { connect } from 'react-redux'


const appSettings = function(state = {}, action) {
  //console.log(action);
  switch (action.type) {
    case 'appSettings_upload':
      let data = action.data;
      for (let key in data.group){
        let value = data.group[key].value;
        let type_id = data.group[key].type_id;
        switch(type_id) {
          case 'integer':
            value = +value;
            break;
          case 'string':
            value = value.toString();
            break;
          case 'js_function':
            value = eval('(' + value + ')');
            break;
          default:
            value = value.toString();
        }
        data.group[key] = value;
      }

      return action.data;
    
    default:
      return state;
  }
}


const pageInfo = function(state = {'request_send': false}, action) {
  switch (action.type) {
    case 'page.title.set':
      return {
        ...state,
        "title": action.data
      };
    case 'data.update':
      return {
        ...state,
        "request_send": action.state
      };

    default:
      return state;
  }
};


const template = function(state = {'sidebar_is_collapsed': false}, action) {
  switch (action.type) {
    case 'sidebar.toogle':
      return {
        ...state,
        "sidebar_is_collapsed": ! state.sidebar_is_collapsed
      };

    default:
      return state;
  }
};



// Combine Reducers
const reducers = combineReducers({
  appSettings:  appSettings,
  pageInfo:     pageInfo,
  template:     template
});

const store = createStore(reducers);

export default store;
