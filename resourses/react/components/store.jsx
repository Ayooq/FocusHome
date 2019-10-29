import {createStore, combineReducers} from 'redux';
import {connect} from 'react-redux'


const appSettings = function (state = {}, action) {
    //console.log(action);
    switch (action.type) {
        case 'appSettings_upload':
            let data = action.data;
            for (let key in data.group) {
                let value = data.group[key].value;
                let type_id = data.group[key].type_id;
                switch (type_id) {
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


const pageInfo = function (state = {'request_send': false}, action) {
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


// const socket = function (state = {}, action) {
//     switch (action.type) {
//         case 'socket.set':
//             return {
//                 ...state,
//                 "socket": action.socket
//             };
//         case 'socket.on':
//             state.socket.on(action.event, msg => {action.func(msg)});
//             break;
//         case 'socket.off':
//             state.socket.off(action.event, msg => {action.func(msg)});
//             break;
//
//         default:
//             return state;
//     }
//     return state;
// };


const template = function (state = {'sidebar_is_collapsed': false,socket_server_state:false}, action) {
    switch (action.type) {
        case 'sidebar.toogle':
            return {
                ...state,
                "sidebar_is_collapsed": !state.sidebar_is_collapsed
            };
        case 'socket_server_state.toogle':
            return {
                ...state,
                "socket_server_state": !state.socket_server_state
            };

        default:
            return state;
    }
};


// Combine Reducers
const reducers = combineReducers({
    appSettings: appSettings,
    pageInfo: pageInfo,
    template: template,
    // socket: socket
});

const store = createStore(reducers);

export default store;
