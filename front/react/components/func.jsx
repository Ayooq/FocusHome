import axios from "axios";

const baseUrl = location.protocol + "//" + location.host;

const myFunc = {
  //ajax
  get: function(parameters) {
    return this._axios("GET", parameters);
  },
  post: function(parameters) {
    return this._axios("POST", parameters);
  },

  _axios: function(method, parameters) {
    //console.log(method + ':' +  _baseUrl + params.url, params);
    axios({
      method,
      baseUrl,
      url: parameters.url,
      params: method === "GET" ? parameters.data || {} : null,
      data: method === "POST" ? parameters.data || {} : null
    })
      .then(response => {
        //console.log('myFunc::get::success - ' + response.status);
        if (typeof parameters.success === "function") {
          return parameters.success(response);
        }
      })
      .catch(function(error) {
        //console.log(error);
        if (typeof parameters.error === "function") {
          return parameters.error(error);
        }
      });
  },

  getUrlParams: function(name) {
    var url = new URL(location.href);
    var p = url.searchParams.get(name);
    return p === undefined ? null : p;
  },

  //cookie
  setCookie: function(key, value) {
    if (!window.localStorage) return null;
    window.localStorage.setItem(key, JSON.stringify(value));
  },

  getCookie: function(key, defaultValue) {
    if (!window.localStorage) return null;
    var data = window.localStorage.getItem(key);
    if (data == null) return defaultValue;
    data = JSON.parse(window.localStorage.getItem(key));
    return data;
  },

  //functions
  //проверка наличия элемента в массиве
  inArray: function(value, array) {
    return array.indexOf(value) != -1;
  },

  //удаление элемента масива по значению
  arrayUnset: function(arr, value) {
    let pos = arr.indexOf(value);
    if (pos != -1) {
      arr.splice(pos, 1);
    }
  },

  //форматирование числа
  numberFormat: function(number, decimals, decimalPoint, thousandsSeparator) {
    number = (number + "").replace(/[^0-9+\-Ee.]/g, "");
    var n = !isFinite(+number) ? 0 : +number,
      prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
      sep =
        typeof thousandsSeparator === "undefined" ? "," : thousandsSeparator,
      dec = typeof decimalPoint === "undefined" ? "." : decimalPoint,
      s = "",
      toFixedFix = function(n, prec) {
        var k = Math.pow(10, prec);
        return "" + Math.round(n * k) / k;
      };
    s = (prec ? toFixedFix(n, prec) : "" + Math.round(n)).split(".");
    if (s[0].length > 3) {
      s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
    }
    if ((s[1] || "").length < prec) {
      s[1] = s[1] || "";
      s[1] += new Array(prec - s[1].length + 1).join("0");
    }
    return s.join(dec);
  }
};

export { myFunc };
