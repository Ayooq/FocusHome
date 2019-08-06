import { createStore, combineReducers } from "redux";
import { connect } from "react-redux";

const mapProps = state => ({});
const mapDispatch = dispatch => ({
  dispatchEvent: event => dispatch(dispatchEvent(event))
});

const appSettings = function(state = {}, action) {
  //console.log(action);
  switch (action.type) {
    case "appSettings":
      let data = action.data;
      for (let key in data.group) {
        let value = data.group[key].value;
        let typeId = data.group[key].datatype_id;
        switch (typeId) {
          case "integer":
            value = +value;
            break;
          case "js_function":
            value = eval("(" + value + ")");
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
};

// The User Reducer
// const profileReducer = function(state = {}, action) {
//   switch (action.type) {
//     case 'ProfileUploaded':
//       return {
//         name:       action.data.name_i + ' ' + action.data.name_f,
//         position:   action.data.position,
//         role:       action.data.role,
//         office_id:  action.data.office_id,
//         image:      ('small' in action.data.image)?action.data.image.small:null,
//         accessList: action.data.accessList
//       }
//
//     default:
//       return state;
//   }
// }

// Combine Reducers
const reducers = combineReducers({
  appSettings
  //clients:      clientsReducer
});

const store = createStore(reducers);

export default store;
