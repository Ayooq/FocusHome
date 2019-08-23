import axios from "axios";

const baseUrl = location.protocol + "//" + location.host;

const utils = {
  get(params) {
    return this._axios("GET", params);
  },
  post(params) {
    return this._axios("POST", params);
  },

  _axios(method, params) {
    //console.log(method + ':' +  _baseUrl + params.url, params);
    axios({
      method,
      baseUrl,
      url: params.url,
      params: method === "GET" ? params.data || {} : null,
      data: method === "POST" ? params.data || {} : null
    })
      .then(response => {
        if (typeof params.success === "function") {
          return params.success(response);
        }
      })
      .catch(error => {
        if (typeof params.error === "function") {
          return params.error(error);
        }
      });
  },

  getUrlParams(name) {
    const url = new URL(location.href);
    const p = url.searchParams.get(name);

    return p === undefined ? null : p;
  },

  getCookie(key, defVal) {
    if (!window.localStorage) return null;
    let data = window.localStorage.getItem(key);
    if (data === null) return defVal;
    data = JSON.parse(window.localStorage.getItem(key));

    return data;
  },

  setCookie(key, val) {
    if (!window.localStorage) return null;
    window.localStorage.setItem(key, JSON.stringify(val));
  },

  // Вернуть позицию элемента в массиве.
  arrayIndex(val, arr) {
    const pos = arr.indexOf(val);

    return arr.indexOf(val) !== -1 ? pos : null;
  },

  // Удаление элемента масива по значению.
  arrayUnset(val, arr) {
    const pos = this.arrayIndex(val, arr);

    if (pos) {
      arr.splice(pos, 1);
    }
  },

  // Форматирование числа.
  numberFormat(number, decimals, decimalPoint, thousandsSep) {
    number = (number + "").replace(/[^0-9+\-Ee.]/g, "");

    let num = !isFinite(+number) ? 0 : +number,
      prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
      sep = typeof thousandsSep === "undefined" ? "," : thousandsSep,
      dec = typeof decimalPoint === "undefined" ? "." : decimalPoint;

    toFixedLength((num, prec) => {
      const k = Math.pow(10, prec);

      return "" + Math.round(num * k) / k;
    });

    let str = (prec ? toFixedLength(num, prec) : "" + Math.round(num)).split(
      "."
    );

    if (str[0].length > 3) {
      str[0] = str[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
    }

    if ((str[1] || "").length < prec) {
      str[1] = str[1] || "";
      str[1] += new Array(prec - str[1].length + 1).join("0");
    }

    return str.join(dec);
  }
};

export default utils;
