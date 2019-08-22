import { createStore, combineReducers } from "redux";

const appSettings = (state = {}, action) => {
  switch (action.type) {
    case "settings":
      const data = action.data;

      for (let key in data.group) {
        let value = data.group[key].value;
        const dataType = data.group[key].datatype__type;

        switch (dataType) {
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

const reducers = combineReducers({
  appSettings
});

const store = createStore(reducers);

export default store;
