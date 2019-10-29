import axios from 'axios';
import store from 'store.jsx';

const _baseUrl = location.protocol + "//" + location.host;

const MyFunc = {
  //ajax
  get: function (params) {
    return this._axios("GET", params);
  },
  post: function (params) {
    return this._axios("POST", params);
  },

  _axios: function (method, params) {
    //console.log(method + ':' +  _baseUrl + params.url, params);
    store.dispatch({
      type: 'data.update',
      state: true
    });
    
    axios({
      method:   method,
      baseURL:  _baseUrl,
      url:      params.url,
      params:   (method === 'GET') ? params.data || {} : null,
      data:     (method === 'POST') ? params.data || {} : null,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-CSRFToken': this.get_csrf(),
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(response => {
      //console.log('MyFunc::get::success - ' + response.status);
      store.dispatch({
        type: 'data.update',
        state: false
      });
      
      if (response.data.title) {
        store.dispatch({
          type: 'page.title.set',
          data: response.data.title
        });
      }
      
      if (typeof params.success === 'function') {
        return params.success(response);
      }
    })
    .catch(function (error) {
      store.dispatch({
        type: 'data.update',
        state: false
      });

      // let status = error.response.status || '';
      // let msg = error.response.statusText || '';
      //
      // if (MyFunc.is_object(error.response.data)){
      //   msg = error.response.data || error.response.statusText;
      // }
      //
      // if (typeof params.error === 'function') {
      //   return params.error(msg);
      // }
      //
      // alert( msg.message || 'error, see console' );
      console.log(error.response)
    });
  },

  getUrlParams: function (name) {
    var url = new URL(location.href);
    var p = url.searchParams.get(name);
    return (p === undefined) ? null : p;
  },



  //cookie
  setCookie: function (key, value) {
    if (!window.localStorage) return null;
    window.localStorage.setItem(key, JSON.stringify(value));
  },

  getCookie: function (key, defaultValue) {
    if (!window.localStorage) return null;
    var data = window.localStorage.getItem(key);
    if (data == null) return defaultValue;
    data = JSON.parse(window.localStorage.getItem(key));
    return data;
  },

  get_csrf: function () {
    var name = 'csrftoken';
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      var value = "; " + document.cookie;
      var parts = value.split("; " + name + "=");
      if (parts.length == 2) return parts.pop().split(";").shift();
    }
    return cookieValue;
  },

  //functions
  //проверка наличия элемента в массиве
  in_array: function (value, array) {
    return (array.indexOf(value) != -1);
  },

  //удаление элемента масива по значению
  array_unset: function(arr, value){
    let pos = arr.indexOf(value);
    if(pos != -1) {
      arr.splice(pos, 1);
    }
  },

  //форматирование числа
  number_format: function(number, decimals, dec_point, thousands_sep) {
  number = (number + '').replace(/[^0-9+\-Ee.]/g, '');
    var n = !isFinite(+number) ? 0 : +number,
      prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
      sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
      dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
      s = '',
      toFixedFix = function (n, prec) {
        var k = Math.pow(10, prec);
        return '' + Math.round(n * k) / k;
      };
    s = (prec ? toFixedFix(n, prec) : '' + Math.round(n)).split('.');
    if (s[0].length > 3) {
      s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
    }
    if ((s[1] || '').length < prec) {
      s[1] = s[1] || '';
      s[1] += new Array(prec - s[1].length + 1).join('0');
    }
    return s.join(dec);
  },

  //рандом
  random: function(min, max)
  {
    return parseInt(Math.random() * (max - min) + min);
  },

  is_array(value){
    return Object.prototype.toString.call(value) === '[object Array]';
  },
  is_object(value){
    return Object.prototype.toString.call(value) === '[object Object]';
  },
  gettype(value){
    return Object.prototype.toString.call(value).replace(']','').split(' ')[1];
  }

};

export {MyFunc};
