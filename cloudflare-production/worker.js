var __defProp = Object.defineProperty;
var __name = (target, value2) => __defProp(target, "name", { value: value2, configurable: true });

// node_modules/@neondatabase/serverless/index.mjs
var Po = Object.create;
var Ie = Object.defineProperty;
var Ro = Object.getOwnPropertyDescriptor;
var Lo = Object.getOwnPropertyNames;
var Bo = Object.getPrototypeOf;
var Fo = Object.prototype.hasOwnProperty;
var Mo = /* @__PURE__ */ __name((r, e, t) => e in r ? Ie(r, e, { enumerable: true, configurable: true, writable: true, value: t }) : r[e] = t, "Mo");
var a = /* @__PURE__ */ __name((r, e) => Ie(r, "name", { value: e, configurable: true }), "a");
var V = /* @__PURE__ */ __name((r, e, t) => () => {
  if (t) throw t[0];
  try {
    return r && (e = r(r = 0)), e;
  } catch (n) {
    throw t = [n], n;
  }
}, "V");
var T = /* @__PURE__ */ __name((r, e) => () => {
  try {
    return e || r((e = { exports: {} }).exports, e), e.exports;
  } catch (t) {
    throw e = 0, t;
  }
}, "T");
var se = /* @__PURE__ */ __name((r, e) => {
  for (var t in e) Ie(r, t, { get: e[t], enumerable: true });
}, "se");
var Dn = /* @__PURE__ */ __name((r, e, t, n) => {
  if (e && typeof e == "object" || typeof e == "function") for (let i of Lo(e)) !Fo.call(r, i) && i !== t && Ie(r, i, { get: /* @__PURE__ */ __name(() => e[i], "get"), enumerable: !(n = Ro(e, i)) || n.enumerable });
  return r;
}, "Dn");
var we = /* @__PURE__ */ __name((r, e, t) => (t = r != null ? Po(Bo(r)) : {}, Dn(e || !r || !r.__esModule ? Ie(t, "default", { value: r, enumerable: true }) : t, r)), "we");
var O = /* @__PURE__ */ __name((r) => Dn(Ie({}, "__esModule", { value: true }), r), "O");
var E = /* @__PURE__ */ __name((r, e, t) => Mo(r, typeof e != "symbol" ? e + "" : e, t), "E");
var Wn = T((lt) => {
  "use strict";
  h();
  lt.byteLength = Oo;
  lt.toByteArray = Qo;
  lt.fromByteArray = No;
  var le = [], X = [], ko = typeof Uint8Array < "u" ? Uint8Array : Array, qt = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
  for (Ae = 0, qn = qt.length; Ae < qn; ++Ae) le[Ae] = qt[Ae], X[qt.charCodeAt(Ae)] = Ae;
  var Ae, qn;
  X[45] = 62;
  X[95] = 63;
  function Nn(r) {
    var e = r.length;
    if (e % 4 > 0) throw new Error("Invalid string. Length must be a multiple of 4");
    var t = r.indexOf("=");
    t === -1 && (t = e);
    var n = t === e ? 0 : 4 - t % 4;
    return [t, n];
  }
  __name(Nn, "Nn");
  a(Nn, "getLens");
  function Oo(r) {
    var e = Nn(r), t = e[0], n = e[1];
    return (t + n) * 3 / 4 - n;
  }
  __name(Oo, "Oo");
  a(Oo, "byteLength");
  function Uo(r, e, t) {
    return (e + t) * 3 / 4 - t;
  }
  __name(Uo, "Uo");
  a(Uo, "_byteLength");
  function Qo(r) {
    var e, t = Nn(r), n = t[0], i = t[1], s = new ko(Uo(r, n, i)), o = 0, u = i > 0 ? n - 4 : n, c;
    for (c = 0; c < u; c += 4) e = X[r.charCodeAt(c)] << 18 | X[r.charCodeAt(c + 1)] << 12 | X[r.charCodeAt(c + 2)] << 6 | X[r.charCodeAt(
      c + 3
    )], s[o++] = e >> 16 & 255, s[o++] = e >> 8 & 255, s[o++] = e & 255;
    return i === 2 && (e = X[r.charCodeAt(c)] << 2 | X[r.charCodeAt(
      c + 1
    )] >> 4, s[o++] = e & 255), i === 1 && (e = X[r.charCodeAt(c)] << 10 | X[r.charCodeAt(c + 1)] << 4 | X[r.charCodeAt(c + 2)] >> 2, s[o++] = e >> 8 & 255, s[o++] = e & 255), s;
  }
  __name(Qo, "Qo");
  a(Qo, "toByteArray");
  function Do(r) {
    return le[r >> 18 & 63] + le[r >> 12 & 63] + le[r >> 6 & 63] + le[r & 63];
  }
  __name(Do, "Do");
  a(Do, "tripletToBase64");
  function qo(r, e, t) {
    for (var n, i = [], s = e; s < t; s += 3) n = (r[s] << 16 & 16711680) + (r[s + 1] << 8 & 65280) + (r[s + 2] & 255), i.push(Do(n));
    return i.join("");
  }
  __name(qo, "qo");
  a(qo, "encodeChunk");
  function No(r) {
    for (var e, t = r.length, n = t % 3, i = [], s = 16383, o = 0, u = t - n; o < u; o += s) i.push(qo(r, o, o + s > u ? u : o + s));
    return n === 1 ? (e = r[t - 1], i.push(le[e >> 2] + le[e << 4 & 63] + "==")) : n === 2 && (e = (r[t - 2] << 8) + r[t - 1], i.push(le[e >> 10] + le[e >> 4 & 63] + le[e << 2 & 63] + "=")), i.join("");
  }
  __name(No, "No");
  a(No, "fromByteArray");
});
var jn = T((Nt) => {
  h();
  Nt.read = function(r, e, t, n, i) {
    var s, o, u = i * 8 - n - 1, c = (1 << u) - 1, l = c >> 1, f = -7, m = t ? i - 1 : 0, g = t ? -1 : 1, w = r[e + m];
    for (m += g, s = w & (1 << -f) - 1, w >>= -f, f += u; f > 0; s = s * 256 + r[e + m], m += g, f -= 8) ;
    for (o = s & (1 << -f) - 1, s >>= -f, f += n; f > 0; o = o * 256 + r[e + m], m += g, f -= 8) ;
    if (s === 0) s = 1 - l;
    else {
      if (s === c) return o ? NaN : (w ? -1 : 1) * (1 / 0);
      o = o + Math.pow(2, n), s = s - l;
    }
    return (w ? -1 : 1) * o * Math.pow(2, s - n);
  };
  Nt.write = function(r, e, t, n, i, s) {
    var o, u, c, l = s * 8 - i - 1, f = (1 << l) - 1, m = f >> 1, g = i === 23 ? Math.pow(2, -24) - Math.pow(2, -77) : 0, w = n ? 0 : s - 1, S = n ? 1 : -1, k = e < 0 || e === 0 && 1 / e < 0 ? 1 : 0;
    for (e = Math.abs(e), isNaN(e) || e === 1 / 0 ? (u = isNaN(e) ? 1 : 0, o = f) : (o = Math.floor(Math.log(e) / Math.LN2), e * (c = Math.pow(2, -o)) < 1 && (o--, c *= 2), o + m >= 1 ? e += g / c : e += g * Math.pow(2, 1 - m), e * c >= 2 && (o++, c /= 2), o + m >= f ? (u = 0, o = f) : o + m >= 1 ? (u = (e * c - 1) * Math.pow(2, i), o = o + m) : (u = e * Math.pow(2, m - 1) * Math.pow(2, i), o = 0)); i >= 8; r[t + w] = u & 255, w += S, u /= 256, i -= 8) ;
    for (o = o << i | u, l += i; l > 0; r[t + w] = o & 255, w += S, o /= 256, l -= 8) ;
    r[t + w - S] |= k * 128;
  };
});
var oi = T((Be) => {
  "use strict";
  h();
  var Wt = Wn(), Re = jn(), Hn = typeof Symbol == "function" && typeof Symbol.for == "function" ? /* @__PURE__ */ Symbol.for("nodejs.util.inspect.custom") : null;
  Be.Buffer = d;
  Be.SlowBuffer = Vo;
  Be.INSPECT_MAX_BYTES = 50;
  var ft = 2147483647;
  Be.kMaxLength = ft;
  d.TYPED_ARRAY_SUPPORT = Wo();
  !d.TYPED_ARRAY_SUPPORT && typeof console < "u" && typeof console.error == "function" && console.error("This browser lacks typed array (Uint8Array) support which is required by `buffer` v5.x. Use `buffer` v4.x if you require old browser support.");
  function Wo() {
    try {
      let r = new Uint8Array(1), e = { foo: a(function() {
        return 42;
      }, "foo") };
      return Object.setPrototypeOf(e, Uint8Array.prototype), Object.setPrototypeOf(r, e), r.foo() === 42;
    } catch {
      return false;
    }
  }
  __name(Wo, "Wo");
  a(Wo, "typedArraySupport");
  Object.defineProperty(d.prototype, "parent", { enumerable: true, get: a(function() {
    if (d.isBuffer(this)) return this.buffer;
  }, "get") });
  Object.defineProperty(d.prototype, "offset", { enumerable: true, get: a(function() {
    if (d.isBuffer(
      this
    )) return this.byteOffset;
  }, "get") });
  function de(r) {
    if (r > ft) throw new RangeError('The value "' + r + '" is invalid for option "size"');
    let e = new Uint8Array(r);
    return Object.setPrototypeOf(e, d.prototype), e;
  }
  __name(de, "de");
  a(de, "createBuffer");
  function d(r, e, t) {
    if (typeof r == "number") {
      if (typeof e == "string") throw new TypeError(
        'The "string" argument must be of type string. Received type number'
      );
      return Gt(r);
    }
    return zn(r, e, t);
  }
  __name(d, "d");
  a(d, "Buffer");
  d.poolSize = 8192;
  function zn(r, e, t) {
    if (typeof r == "string") return Ho(r, e);
    if (ArrayBuffer.isView(r)) return $o(r);
    if (r == null) throw new TypeError("The first argument must be one of type string, Buffer, ArrayBuffer, Array, or Array-like Object. Received type " + typeof r);
    if (fe(r, ArrayBuffer) || r && fe(r.buffer, ArrayBuffer) || typeof SharedArrayBuffer < "u" && (fe(r, SharedArrayBuffer) || r && fe(
      r.buffer,
      SharedArrayBuffer
    ))) return Ht(r, e, t);
    if (typeof r == "number") throw new TypeError('The "value" argument must not be of type number. Received type number');
    let n = r.valueOf && r.valueOf();
    if (n != null && n !== r) return d.from(n, e, t);
    let i = Go(r);
    if (i) return i;
    if (typeof Symbol < "u" && Symbol.toPrimitive != null && typeof r[Symbol.toPrimitive] == "function") return d.from(r[Symbol.toPrimitive]("string"), e, t);
    throw new TypeError("The first argument must be one of type string, Buffer, ArrayBuffer, Array, or Array-like Object. Received type " + typeof r);
  }
  __name(zn, "zn");
  a(zn, "from");
  d.from = function(r, e, t) {
    return zn(r, e, t);
  };
  Object.setPrototypeOf(
    d.prototype,
    Uint8Array.prototype
  );
  Object.setPrototypeOf(d, Uint8Array);
  function Kn(r) {
    if (typeof r != "number") throw new TypeError(
      '"size" argument must be of type number'
    );
    if (r < 0) throw new RangeError('The value "' + r + '" is invalid for option "size"');
  }
  __name(Kn, "Kn");
  a(Kn, "assertSize");
  function jo(r, e, t) {
    return Kn(r), r <= 0 ? de(r) : e !== void 0 ? typeof t == "string" ? de(r).fill(e, t) : de(r).fill(e) : de(r);
  }
  __name(jo, "jo");
  a(jo, "alloc");
  d.alloc = function(r, e, t) {
    return jo(r, e, t);
  };
  function Gt(r) {
    return Kn(r), de(r < 0 ? 0 : Vt(r) | 0);
  }
  __name(Gt, "Gt");
  a(Gt, "allocUnsafe");
  d.allocUnsafe = function(r) {
    return Gt(
      r
    );
  };
  d.allocUnsafeSlow = function(r) {
    return Gt(r);
  };
  function Ho(r, e) {
    if ((typeof e != "string" || e === "") && (e = "utf8"), !d.isEncoding(e)) throw new TypeError("Unknown encoding: " + e);
    let t = Yn(r, e) | 0, n = de(t), i = n.write(
      r,
      e
    );
    return i !== t && (n = n.slice(0, i)), n;
  }
  __name(Ho, "Ho");
  a(Ho, "fromString");
  function jt(r) {
    let e = r.length < 0 ? 0 : Vt(r.length) | 0, t = de(e);
    for (let n = 0; n < e; n += 1) t[n] = r[n] & 255;
    return t;
  }
  __name(jt, "jt");
  a(jt, "fromArrayLike");
  function $o(r) {
    if (fe(r, Uint8Array)) {
      let e = new Uint8Array(r);
      return Ht(e.buffer, e.byteOffset, e.byteLength);
    }
    return jt(r);
  }
  __name($o, "$o");
  a($o, "fromArrayView");
  function Ht(r, e, t) {
    if (e < 0 || r.byteLength < e) throw new RangeError('"offset" is outside of buffer bounds');
    if (r.byteLength < e + (t || 0)) throw new RangeError('"length" is outside of buffer bounds');
    let n;
    return e === void 0 && t === void 0 ? n = new Uint8Array(r) : t === void 0 ? n = new Uint8Array(r, e) : n = new Uint8Array(
      r,
      e,
      t
    ), Object.setPrototypeOf(n, d.prototype), n;
  }
  __name(Ht, "Ht");
  a(Ht, "fromArrayBuffer");
  function Go(r) {
    if (d.isBuffer(r)) {
      let e = Vt(r.length) | 0, t = de(e);
      return t.length === 0 || r.copy(t, 0, 0, e), t;
    }
    if (r.length !== void 0) return typeof r.length != "number" || Kt(r.length) ? de(0) : jt(r);
    if (r.type === "Buffer" && Array.isArray(r.data)) return jt(r.data);
  }
  __name(Go, "Go");
  a(Go, "fromObject");
  function Vt(r) {
    if (r >= ft) throw new RangeError("Attempt to allocate Buffer larger than maximum size: 0x" + ft.toString(16) + " bytes");
    return r | 0;
  }
  __name(Vt, "Vt");
  a(Vt, "checked");
  function Vo(r) {
    return +r != r && (r = 0), d.alloc(+r);
  }
  __name(Vo, "Vo");
  a(Vo, "SlowBuffer");
  d.isBuffer = a(function(e) {
    return e != null && e._isBuffer === true && e !== d.prototype;
  }, "isBuffer");
  d.compare = a(function(e, t) {
    if (fe(e, Uint8Array) && (e = d.from(e, e.offset, e.byteLength)), fe(t, Uint8Array) && (t = d.from(t, t.offset, t.byteLength)), !d.isBuffer(e) || !d.isBuffer(t)) throw new TypeError(
      'The "buf1", "buf2" arguments must be one of type Buffer or Uint8Array'
    );
    if (e === t) return 0;
    let n = e.length, i = t.length;
    for (let s = 0, o = Math.min(n, i); s < o; ++s) if (e[s] !== t[s]) {
      n = e[s], i = t[s];
      break;
    }
    return n < i ? -1 : i < n ? 1 : 0;
  }, "compare");
  d.isEncoding = a(function(e) {
    switch (String(e).toLowerCase()) {
      case "hex":
      case "utf8":
      case "utf-8":
      case "ascii":
      case "latin1":
      case "binary":
      case "base64":
      case "ucs2":
      case "ucs-2":
      case "utf16le":
      case "utf-16le":
        return true;
      default:
        return false;
    }
  }, "isEncoding");
  d.concat = a(function(e, t) {
    if (!Array.isArray(e)) throw new TypeError(
      '"list" argument must be an Array of Buffers'
    );
    if (e.length === 0) return d.alloc(0);
    let n;
    if (t === void 0)
      for (t = 0, n = 0; n < e.length; ++n) t += e[n].length;
    let i = d.allocUnsafe(t), s = 0;
    for (n = 0; n < e.length; ++n) {
      let o = e[n];
      if (fe(o, Uint8Array)) s + o.length > i.length ? (d.isBuffer(o) || (o = d.from(o)), o.copy(i, s)) : Uint8Array.prototype.set.call(i, o, s);
      else if (d.isBuffer(o)) o.copy(i, s);
      else throw new TypeError('"list" argument must be an Array of Buffers');
      s += o.length;
    }
    return i;
  }, "concat");
  function Yn(r, e) {
    if (d.isBuffer(r)) return r.length;
    if (ArrayBuffer.isView(r) || fe(r, ArrayBuffer)) return r.byteLength;
    if (typeof r != "string") throw new TypeError(
      'The "string" argument must be one of type string, Buffer, or ArrayBuffer. Received type ' + typeof r
    );
    let t = r.length, n = arguments.length > 2 && arguments[2] === true;
    if (!n && t === 0) return 0;
    let i = false;
    for (; ; ) switch (e) {
      case "ascii":
      case "latin1":
      case "binary":
        return t;
      case "utf8":
      case "utf-8":
        return $t(r).length;
      case "ucs2":
      case "ucs-2":
      case "utf16le":
      case "utf-16le":
        return t * 2;
      case "hex":
        return t >>> 1;
      case "base64":
        return si(r).length;
      default:
        if (i) return n ? -1 : $t(r).length;
        e = ("" + e).toLowerCase(), i = true;
    }
  }
  __name(Yn, "Yn");
  a(Yn, "byteLength");
  d.byteLength = Yn;
  function zo(r, e, t) {
    let n = false;
    if ((e === void 0 || e < 0) && (e = 0), e > this.length || ((t === void 0 || t > this.length) && (t = this.length), t <= 0) || (t >>>= 0, e >>>= 0, t <= e)) return "";
    for (r || (r = "utf8"); ; ) switch (r) {
      case "hex":
        return ia(this, e, t);
      case "utf8":
      case "utf-8":
        return Jn(this, e, t);
      case "ascii":
        return ra(this, e, t);
      case "latin1":
      case "binary":
        return na(
          this,
          e,
          t
        );
      case "base64":
        return ea(this, e, t);
      case "ucs2":
      case "ucs-2":
      case "utf16le":
      case "utf-16le":
        return sa(
          this,
          e,
          t
        );
      default:
        if (n) throw new TypeError("Unknown encoding: " + r);
        r = (r + "").toLowerCase(), n = true;
    }
  }
  __name(zo, "zo");
  a(
    zo,
    "slowToString"
  );
  d.prototype._isBuffer = true;
  function Ce(r, e, t) {
    let n = r[e];
    r[e] = r[t], r[t] = n;
  }
  __name(Ce, "Ce");
  a(Ce, "swap");
  d.prototype.swap16 = a(function() {
    let e = this.length;
    if (e % 2 !== 0) throw new RangeError("Buffer size must be a multiple of 16-bits");
    for (let t = 0; t < e; t += 2) Ce(this, t, t + 1);
    return this;
  }, "swap16");
  d.prototype.swap32 = a(function() {
    let e = this.length;
    if (e % 4 !== 0) throw new RangeError("Buffer size must be a multiple of 32-bits");
    for (let t = 0; t < e; t += 4) Ce(this, t, t + 3), Ce(this, t + 1, t + 2);
    return this;
  }, "swap32");
  d.prototype.swap64 = a(
    function() {
      let e = this.length;
      if (e % 8 !== 0) throw new RangeError("Buffer size must be a multiple of 64-bits");
      for (let t = 0; t < e; t += 8) Ce(this, t, t + 7), Ce(this, t + 1, t + 6), Ce(this, t + 2, t + 5), Ce(this, t + 3, t + 4);
      return this;
    },
    "swap64"
  );
  d.prototype.toString = a(function() {
    let e = this.length;
    return e === 0 ? "" : arguments.length === 0 ? Jn(
      this,
      0,
      e
    ) : zo.apply(this, arguments);
  }, "toString");
  d.prototype.toLocaleString = d.prototype.toString;
  d.prototype.equals = a(function(e) {
    if (!d.isBuffer(e)) throw new TypeError("Argument must be a Buffer");
    return this === e ? true : d.compare(this, e) === 0;
  }, "equals");
  d.prototype.inspect = a(function() {
    let e = "", t = Be.INSPECT_MAX_BYTES;
    return e = this.toString("hex", 0, t).replace(/(.{2})/g, "$1 ").trim(), this.length > t && (e += " ... "), "<Buffer " + e + ">";
  }, "inspect");
  Hn && (d.prototype[Hn] = d.prototype.inspect);
  d.prototype.compare = a(function(e, t, n, i, s) {
    if (fe(e, Uint8Array) && (e = d.from(e, e.offset, e.byteLength)), !d.isBuffer(e)) throw new TypeError('The "target" argument must be one of type Buffer or Uint8Array. Received type ' + typeof e);
    if (t === void 0 && (t = 0), n === void 0 && (n = e ? e.length : 0), i === void 0 && (i = 0), s === void 0 && (s = this.length), t < 0 || n > e.length || i < 0 || s > this.length) throw new RangeError("out of range index");
    if (i >= s && t >= n) return 0;
    if (i >= s) return -1;
    if (t >= n) return 1;
    if (t >>>= 0, n >>>= 0, i >>>= 0, s >>>= 0, this === e) return 0;
    let o = s - i, u = n - t, c = Math.min(o, u), l = this.slice(
      i,
      s
    ), f = e.slice(t, n);
    for (let m = 0; m < c; ++m) if (l[m] !== f[m]) {
      o = l[m], u = f[m];
      break;
    }
    return o < u ? -1 : u < o ? 1 : 0;
  }, "compare");
  function Zn(r, e, t, n, i) {
    if (r.length === 0) return -1;
    if (typeof t == "string" ? (n = t, t = 0) : t > 2147483647 ? t = 2147483647 : t < -2147483648 && (t = -2147483648), t = +t, Kt(t) && (t = i ? 0 : r.length - 1), t < 0 && (t = r.length + t), t >= r.length) {
      if (i) return -1;
      t = r.length - 1;
    } else if (t < 0) if (i) t = 0;
    else return -1;
    if (typeof e == "string" && (e = d.from(
      e,
      n
    )), d.isBuffer(e)) return e.length === 0 ? -1 : $n(r, e, t, n, i);
    if (typeof e == "number") return e = e & 255, typeof Uint8Array.prototype.indexOf == "function" ? i ? Uint8Array.prototype.indexOf.call(r, e, t) : Uint8Array.prototype.lastIndexOf.call(r, e, t) : $n(r, [e], t, n, i);
    throw new TypeError("val must be string, number or Buffer");
  }
  __name(Zn, "Zn");
  a(Zn, "bidirectionalIndexOf");
  function $n(r, e, t, n, i) {
    let s = 1, o = r.length, u = e.length;
    if (n !== void 0 && (n = String(n).toLowerCase(), n === "ucs2" || n === "ucs-2" || n === "utf16le" || n === "utf-16le")) {
      if (r.length < 2 || e.length < 2) return -1;
      s = 2, o /= 2, u /= 2, t /= 2;
    }
    function c(f, m) {
      return s === 1 ? f[m] : f.readUInt16BE(m * s);
    }
    __name(c, "c");
    a(c, "read");
    let l;
    if (i) {
      let f = -1;
      for (l = t; l < o; l++) if (c(r, l) === c(e, f === -1 ? 0 : l - f)) {
        if (f === -1 && (f = l), l - f + 1 === u) return f * s;
      } else f !== -1 && (l -= l - f), f = -1;
    } else for (t + u > o && (t = o - u), l = t; l >= 0; l--) {
      let f = true;
      for (let m = 0; m < u; m++) if (c(r, l + m) !== c(e, m)) {
        f = false;
        break;
      }
      if (f) return l;
    }
    return -1;
  }
  __name($n, "$n");
  a($n, "arrayIndexOf");
  d.prototype.includes = a(function(e, t, n) {
    return this.indexOf(
      e,
      t,
      n
    ) !== -1;
  }, "includes");
  d.prototype.indexOf = a(function(e, t, n) {
    return Zn(this, e, t, n, true);
  }, "indexOf");
  d.prototype.lastIndexOf = a(function(e, t, n) {
    return Zn(this, e, t, n, false);
  }, "lastIndexOf");
  function Ko(r, e, t, n) {
    t = Number(t) || 0;
    let i = r.length - t;
    n ? (n = Number(n), n > i && (n = i)) : n = i;
    let s = e.length;
    n > s / 2 && (n = s / 2);
    let o;
    for (o = 0; o < n; ++o) {
      let u = parseInt(e.substr(o * 2, 2), 16);
      if (Kt(u)) return o;
      r[t + o] = u;
    }
    return o;
  }
  __name(Ko, "Ko");
  a(Ko, "hexWrite");
  function Yo(r, e, t, n) {
    return ht($t(e, r.length - t), r, t, n);
  }
  __name(Yo, "Yo");
  a(Yo, "utf8Write");
  function Zo(r, e, t, n) {
    return ht(ca(e), r, t, n);
  }
  __name(Zo, "Zo");
  a(
    Zo,
    "asciiWrite"
  );
  function Jo(r, e, t, n) {
    return ht(si(e), r, t, n);
  }
  __name(Jo, "Jo");
  a(Jo, "base64Write");
  function Xo(r, e, t, n) {
    return ht(
      la(e, r.length - t),
      r,
      t,
      n
    );
  }
  __name(Xo, "Xo");
  a(Xo, "ucs2Write");
  d.prototype.write = a(function(e, t, n, i) {
    if (t === void 0) i = "utf8", n = this.length, t = 0;
    else if (n === void 0 && typeof t == "string") i = t, n = this.length, t = 0;
    else if (isFinite(t))
      t = t >>> 0, isFinite(n) ? (n = n >>> 0, i === void 0 && (i = "utf8")) : (i = n, n = void 0);
    else throw new Error("Buffer.write(string, encoding, offset[, length]) is no longer supported");
    let s = this.length - t;
    if ((n === void 0 || n > s) && (n = s), e.length > 0 && (n < 0 || t < 0) || t > this.length) throw new RangeError("Attempt to write outside buffer bounds");
    i || (i = "utf8");
    let o = false;
    for (; ; ) switch (i) {
      case "hex":
        return Ko(this, e, t, n);
      case "utf8":
      case "utf-8":
        return Yo(this, e, t, n);
      case "ascii":
      case "latin1":
      case "binary":
        return Zo(this, e, t, n);
      case "base64":
        return Jo(this, e, t, n);
      case "ucs2":
      case "ucs-2":
      case "utf16le":
      case "utf-16le":
        return Xo(this, e, t, n);
      default:
        if (o) throw new TypeError("Unknown encoding: " + i);
        i = ("" + i).toLowerCase(), o = true;
    }
  }, "write");
  d.prototype.toJSON = a(function() {
    return { type: "Buffer", data: Array.prototype.slice.call(this._arr || this, 0) };
  }, "toJSON");
  function ea(r, e, t) {
    return e === 0 && t === r.length ? Wt.fromByteArray(r) : Wt.fromByteArray(r.slice(e, t));
  }
  __name(ea, "ea");
  a(ea, "base64Slice");
  function Jn(r, e, t) {
    t = Math.min(r.length, t);
    let n = [], i = e;
    for (; i < t; ) {
      let s = r[i], o = null, u = s > 239 ? 4 : s > 223 ? 3 : s > 191 ? 2 : 1;
      if (i + u <= t) {
        let c, l, f, m;
        switch (u) {
          case 1:
            s < 128 && (o = s);
            break;
          case 2:
            c = r[i + 1], (c & 192) === 128 && (m = (s & 31) << 6 | c & 63, m > 127 && (o = m));
            break;
          case 3:
            c = r[i + 1], l = r[i + 2], (c & 192) === 128 && (l & 192) === 128 && (m = (s & 15) << 12 | (c & 63) << 6 | l & 63, m > 2047 && (m < 55296 || m > 57343) && (o = m));
            break;
          case 4:
            c = r[i + 1], l = r[i + 2], f = r[i + 3], (c & 192) === 128 && (l & 192) === 128 && (f & 192) === 128 && (m = (s & 15) << 18 | (c & 63) << 12 | (l & 63) << 6 | f & 63, m > 65535 && m < 1114112 && (o = m));
        }
      }
      o === null ? (o = 65533, u = 1) : o > 65535 && (o -= 65536, n.push(o >>> 10 & 1023 | 55296), o = 56320 | o & 1023), n.push(o), i += u;
    }
    return ta(n);
  }
  __name(Jn, "Jn");
  a(Jn, "utf8Slice");
  var Gn = 4096;
  function ta(r) {
    let e = r.length;
    if (e <= Gn) return String.fromCharCode.apply(String, r);
    let t = "", n = 0;
    for (; n < e; ) t += String.fromCharCode.apply(String, r.slice(n, n += Gn));
    return t;
  }
  __name(ta, "ta");
  a(ta, "decodeCodePointsArray");
  function ra(r, e, t) {
    let n = "";
    t = Math.min(r.length, t);
    for (let i = e; i < t; ++i) n += String.fromCharCode(r[i] & 127);
    return n;
  }
  __name(ra, "ra");
  a(ra, "asciiSlice");
  function na(r, e, t) {
    let n = "";
    t = Math.min(r.length, t);
    for (let i = e; i < t; ++i) n += String.fromCharCode(r[i]);
    return n;
  }
  __name(na, "na");
  a(na, "latin1Slice");
  function ia(r, e, t) {
    let n = r.length;
    (!e || e < 0) && (e = 0), (!t || t < 0 || t > n) && (t = n);
    let i = "";
    for (let s = e; s < t; ++s) i += fa[r[s]];
    return i;
  }
  __name(ia, "ia");
  a(ia, "hexSlice");
  function sa(r, e, t) {
    let n = r.slice(e, t), i = "";
    for (let s = 0; s < n.length - 1; s += 2) i += String.fromCharCode(n[s] + n[s + 1] * 256);
    return i;
  }
  __name(sa, "sa");
  a(sa, "utf16leSlice");
  d.prototype.slice = a(function(e, t) {
    let n = this.length;
    e = ~~e, t = t === void 0 ? n : ~~t, e < 0 ? (e += n, e < 0 && (e = 0)) : e > n && (e = n), t < 0 ? (t += n, t < 0 && (t = 0)) : t > n && (t = n), t < e && (t = e);
    let i = this.subarray(e, t);
    return Object.setPrototypeOf(i, d.prototype), i;
  }, "slice");
  function U(r, e, t) {
    if (r % 1 !== 0 || r < 0) throw new RangeError("offset is not uint");
    if (r + e > t) throw new RangeError("Trying to access beyond buffer length");
  }
  __name(U, "U");
  a(U, "checkOffset");
  d.prototype.readUintLE = d.prototype.readUIntLE = a(
    function(e, t, n) {
      e = e >>> 0, t = t >>> 0, n || U(e, t, this.length);
      let i = this[e], s = 1, o = 0;
      for (; ++o < t && (s *= 256); ) i += this[e + o] * s;
      return i;
    },
    "readUIntLE"
  );
  d.prototype.readUintBE = d.prototype.readUIntBE = a(function(e, t, n) {
    e = e >>> 0, t = t >>> 0, n || U(
      e,
      t,
      this.length
    );
    let i = this[e + --t], s = 1;
    for (; t > 0 && (s *= 256); ) i += this[e + --t] * s;
    return i;
  }, "readUIntBE");
  d.prototype.readUint8 = d.prototype.readUInt8 = a(
    function(e, t) {
      return e = e >>> 0, t || U(e, 1, this.length), this[e];
    },
    "readUInt8"
  );
  d.prototype.readUint16LE = d.prototype.readUInt16LE = a(function(e, t) {
    return e = e >>> 0, t || U(
      e,
      2,
      this.length
    ), this[e] | this[e + 1] << 8;
  }, "readUInt16LE");
  d.prototype.readUint16BE = d.prototype.readUInt16BE = a(function(e, t) {
    return e = e >>> 0, t || U(e, 2, this.length), this[e] << 8 | this[e + 1];
  }, "readUInt16BE");
  d.prototype.readUint32LE = d.prototype.readUInt32LE = a(function(e, t) {
    return e = e >>> 0, t || U(e, 4, this.length), (this[e] | this[e + 1] << 8 | this[e + 2] << 16) + this[e + 3] * 16777216;
  }, "readUInt32LE");
  d.prototype.readUint32BE = d.prototype.readUInt32BE = a(function(e, t) {
    return e = e >>> 0, t || U(e, 4, this.length), this[e] * 16777216 + (this[e + 1] << 16 | this[e + 2] << 8 | this[e + 3]);
  }, "readUInt32BE");
  d.prototype.readBigUInt64LE = be(a(function(e) {
    e = e >>> 0, Le(e, "offset");
    let t = this[e], n = this[e + 7];
    (t === void 0 || n === void 0) && We(e, this.length - 8);
    let i = t + this[++e] * 2 ** 8 + this[++e] * 2 ** 16 + this[++e] * 2 ** 24, s = this[++e] + this[++e] * 2 ** 8 + this[++e] * 2 ** 16 + n * 2 ** 24;
    return BigInt(i) + (BigInt(s) << BigInt(32));
  }, "readBigUInt64LE"));
  d.prototype.readBigUInt64BE = be(a(function(e) {
    e = e >>> 0, Le(e, "offset");
    let t = this[e], n = this[e + 7];
    (t === void 0 || n === void 0) && We(e, this.length - 8);
    let i = t * 2 ** 24 + this[++e] * 2 ** 16 + this[++e] * 2 ** 8 + this[++e], s = this[++e] * 2 ** 24 + this[++e] * 2 ** 16 + this[++e] * 2 ** 8 + n;
    return (BigInt(i) << BigInt(
      32
    )) + BigInt(s);
  }, "readBigUInt64BE"));
  d.prototype.readIntLE = a(function(e, t, n) {
    e = e >>> 0, t = t >>> 0, n || U(
      e,
      t,
      this.length
    );
    let i = this[e], s = 1, o = 0;
    for (; ++o < t && (s *= 256); ) i += this[e + o] * s;
    return s *= 128, i >= s && (i -= Math.pow(2, 8 * t)), i;
  }, "readIntLE");
  d.prototype.readIntBE = a(function(e, t, n) {
    e = e >>> 0, t = t >>> 0, n || U(e, t, this.length);
    let i = t, s = 1, o = this[e + --i];
    for (; i > 0 && (s *= 256); ) o += this[e + --i] * s;
    return s *= 128, o >= s && (o -= Math.pow(2, 8 * t)), o;
  }, "readIntBE");
  d.prototype.readInt8 = a(function(e, t) {
    return e = e >>> 0, t || U(e, 1, this.length), this[e] & 128 ? (255 - this[e] + 1) * -1 : this[e];
  }, "readInt8");
  d.prototype.readInt16LE = a(function(e, t) {
    e = e >>> 0, t || U(
      e,
      2,
      this.length
    );
    let n = this[e] | this[e + 1] << 8;
    return n & 32768 ? n | 4294901760 : n;
  }, "readInt16LE");
  d.prototype.readInt16BE = a(function(e, t) {
    e = e >>> 0, t || U(e, 2, this.length);
    let n = this[e + 1] | this[e] << 8;
    return n & 32768 ? n | 4294901760 : n;
  }, "readInt16BE");
  d.prototype.readInt32LE = a(function(e, t) {
    return e = e >>> 0, t || U(e, 4, this.length), this[e] | this[e + 1] << 8 | this[e + 2] << 16 | this[e + 3] << 24;
  }, "readInt32LE");
  d.prototype.readInt32BE = a(function(e, t) {
    return e = e >>> 0, t || U(e, 4, this.length), this[e] << 24 | this[e + 1] << 16 | this[e + 2] << 8 | this[e + 3];
  }, "readInt32BE");
  d.prototype.readBigInt64LE = be(a(function(e) {
    e = e >>> 0, Le(e, "offset");
    let t = this[e], n = this[e + 7];
    (t === void 0 || n === void 0) && We(e, this.length - 8);
    let i = this[e + 4] + this[e + 5] * 2 ** 8 + this[e + 6] * 2 ** 16 + (n << 24);
    return (BigInt(i) << BigInt(
      32
    )) + BigInt(t + this[++e] * 2 ** 8 + this[++e] * 2 ** 16 + this[++e] * 2 ** 24);
  }, "readBigInt64LE"));
  d.prototype.readBigInt64BE = be(a(function(e) {
    e = e >>> 0, Le(e, "offset");
    let t = this[e], n = this[e + 7];
    (t === void 0 || n === void 0) && We(e, this.length - 8);
    let i = (t << 24) + this[++e] * 2 ** 16 + this[++e] * 2 ** 8 + this[++e];
    return (BigInt(i) << BigInt(32)) + BigInt(
      this[++e] * 2 ** 24 + this[++e] * 2 ** 16 + this[++e] * 2 ** 8 + n
    );
  }, "readBigInt64BE"));
  d.prototype.readFloatLE = a(function(e, t) {
    return e = e >>> 0, t || U(e, 4, this.length), Re.read(this, e, true, 23, 4);
  }, "readFloatLE");
  d.prototype.readFloatBE = a(function(e, t) {
    return e = e >>> 0, t || U(e, 4, this.length), Re.read(this, e, false, 23, 4);
  }, "readFloatBE");
  d.prototype.readDoubleLE = a(function(e, t) {
    return e = e >>> 0, t || U(e, 8, this.length), Re.read(this, e, true, 52, 8);
  }, "readDoubleLE");
  d.prototype.readDoubleBE = a(function(e, t) {
    return e = e >>> 0, t || U(e, 8, this.length), Re.read(
      this,
      e,
      false,
      52,
      8
    );
  }, "readDoubleBE");
  function z(r, e, t, n, i, s) {
    if (!d.isBuffer(r)) throw new TypeError('"buffer" argument must be a Buffer instance');
    if (e > i || e < s) throw new RangeError('"value" argument is out of bounds');
    if (t + n > r.length) throw new RangeError("Index out of range");
  }
  __name(z, "z");
  a(z, "checkInt");
  d.prototype.writeUintLE = d.prototype.writeUIntLE = a(function(e, t, n, i) {
    if (e = +e, t = t >>> 0, n = n >>> 0, !i) {
      let u = Math.pow(2, 8 * n) - 1;
      z(
        this,
        e,
        t,
        n,
        u,
        0
      );
    }
    let s = 1, o = 0;
    for (this[t] = e & 255; ++o < n && (s *= 256); ) this[t + o] = e / s & 255;
    return t + n;
  }, "writeUIntLE");
  d.prototype.writeUintBE = d.prototype.writeUIntBE = a(function(e, t, n, i) {
    if (e = +e, t = t >>> 0, n = n >>> 0, !i) {
      let u = Math.pow(2, 8 * n) - 1;
      z(this, e, t, n, u, 0);
    }
    let s = n - 1, o = 1;
    for (this[t + s] = e & 255; --s >= 0 && (o *= 256); ) this[t + s] = e / o & 255;
    return t + n;
  }, "writeUIntBE");
  d.prototype.writeUint8 = d.prototype.writeUInt8 = a(function(e, t, n) {
    return e = +e, t = t >>> 0, n || z(this, e, t, 1, 255, 0), this[t] = e & 255, t + 1;
  }, "writeUInt8");
  d.prototype.writeUint16LE = d.prototype.writeUInt16LE = a(function(e, t, n) {
    return e = +e, t = t >>> 0, n || z(this, e, t, 2, 65535, 0), this[t] = e & 255, this[t + 1] = e >>> 8, t + 2;
  }, "writeUInt16LE");
  d.prototype.writeUint16BE = d.prototype.writeUInt16BE = a(function(e, t, n) {
    return e = +e, t = t >>> 0, n || z(this, e, t, 2, 65535, 0), this[t] = e >>> 8, this[t + 1] = e & 255, t + 2;
  }, "writeUInt16BE");
  d.prototype.writeUint32LE = d.prototype.writeUInt32LE = a(function(e, t, n) {
    return e = +e, t = t >>> 0, n || z(
      this,
      e,
      t,
      4,
      4294967295,
      0
    ), this[t + 3] = e >>> 24, this[t + 2] = e >>> 16, this[t + 1] = e >>> 8, this[t] = e & 255, t + 4;
  }, "writeUInt32LE");
  d.prototype.writeUint32BE = d.prototype.writeUInt32BE = a(function(e, t, n) {
    return e = +e, t = t >>> 0, n || z(
      this,
      e,
      t,
      4,
      4294967295,
      0
    ), this[t] = e >>> 24, this[t + 1] = e >>> 16, this[t + 2] = e >>> 8, this[t + 3] = e & 255, t + 4;
  }, "writeUInt32BE");
  function Xn(r, e, t, n, i) {
    ii(e, n, i, r, t, 7);
    let s = Number(e & BigInt(4294967295));
    r[t++] = s, s = s >> 8, r[t++] = s, s = s >> 8, r[t++] = s, s = s >> 8, r[t++] = s;
    let o = Number(e >> BigInt(32) & BigInt(4294967295));
    return r[t++] = o, o = o >> 8, r[t++] = o, o = o >> 8, r[t++] = o, o = o >> 8, r[t++] = o, t;
  }
  __name(Xn, "Xn");
  a(Xn, "wrtBigUInt64LE");
  function ei(r, e, t, n, i) {
    ii(e, n, i, r, t, 7);
    let s = Number(e & BigInt(4294967295));
    r[t + 7] = s, s = s >> 8, r[t + 6] = s, s = s >> 8, r[t + 5] = s, s = s >> 8, r[t + 4] = s;
    let o = Number(e >> BigInt(32) & BigInt(4294967295));
    return r[t + 3] = o, o = o >> 8, r[t + 2] = o, o = o >> 8, r[t + 1] = o, o = o >> 8, r[t] = o, t + 8;
  }
  __name(ei, "ei");
  a(ei, "wrtBigUInt64BE");
  d.prototype.writeBigUInt64LE = be(a(function(e, t = 0) {
    return Xn(this, e, t, BigInt(0), BigInt("0xffffffffffffffff"));
  }, "writeBigUInt64LE"));
  d.prototype.writeBigUInt64BE = be(a(function(e, t = 0) {
    return ei(this, e, t, BigInt(0), BigInt(
      "0xffffffffffffffff"
    ));
  }, "writeBigUInt64BE"));
  d.prototype.writeIntLE = a(function(e, t, n, i) {
    if (e = +e, t = t >>> 0, !i) {
      let c = Math.pow(2, 8 * n - 1);
      z(this, e, t, n, c - 1, -c);
    }
    let s = 0, o = 1, u = 0;
    for (this[t] = e & 255; ++s < n && (o *= 256); )
      e < 0 && u === 0 && this[t + s - 1] !== 0 && (u = 1), this[t + s] = (e / o >> 0) - u & 255;
    return t + n;
  }, "writeIntLE");
  d.prototype.writeIntBE = a(function(e, t, n, i) {
    if (e = +e, t = t >>> 0, !i) {
      let c = Math.pow(2, 8 * n - 1);
      z(this, e, t, n, c - 1, -c);
    }
    let s = n - 1, o = 1, u = 0;
    for (this[t + s] = e & 255; --s >= 0 && (o *= 256); ) e < 0 && u === 0 && this[t + s + 1] !== 0 && (u = 1), this[t + s] = (e / o >> 0) - u & 255;
    return t + n;
  }, "writeIntBE");
  d.prototype.writeInt8 = a(function(e, t, n) {
    return e = +e, t = t >>> 0, n || z(this, e, t, 1, 127, -128), e < 0 && (e = 255 + e + 1), this[t] = e & 255, t + 1;
  }, "writeInt8");
  d.prototype.writeInt16LE = a(function(e, t, n) {
    return e = +e, t = t >>> 0, n || z(this, e, t, 2, 32767, -32768), this[t] = e & 255, this[t + 1] = e >>> 8, t + 2;
  }, "writeInt16LE");
  d.prototype.writeInt16BE = a(function(e, t, n) {
    return e = +e, t = t >>> 0, n || z(this, e, t, 2, 32767, -32768), this[t] = e >>> 8, this[t + 1] = e & 255, t + 2;
  }, "writeInt16BE");
  d.prototype.writeInt32LE = a(function(e, t, n) {
    return e = +e, t = t >>> 0, n || z(
      this,
      e,
      t,
      4,
      2147483647,
      -2147483648
    ), this[t] = e & 255, this[t + 1] = e >>> 8, this[t + 2] = e >>> 16, this[t + 3] = e >>> 24, t + 4;
  }, "writeInt32LE");
  d.prototype.writeInt32BE = a(function(e, t, n) {
    return e = +e, t = t >>> 0, n || z(
      this,
      e,
      t,
      4,
      2147483647,
      -2147483648
    ), e < 0 && (e = 4294967295 + e + 1), this[t] = e >>> 24, this[t + 1] = e >>> 16, this[t + 2] = e >>> 8, this[t + 3] = e & 255, t + 4;
  }, "writeInt32BE");
  d.prototype.writeBigInt64LE = be(a(function(e, t = 0) {
    return Xn(this, e, t, -BigInt("0x8000000000000000"), BigInt("0x7fffffffffffffff"));
  }, "writeBigInt64LE"));
  d.prototype.writeBigInt64BE = be(
    a(function(e, t = 0) {
      return ei(this, e, t, -BigInt("0x8000000000000000"), BigInt("0x7fffffffffffffff"));
    }, "writeBigInt64BE")
  );
  function ti(r, e, t, n, i, s) {
    if (t + n > r.length) throw new RangeError("Index out of range");
    if (t < 0) throw new RangeError("Index out of range");
  }
  __name(ti, "ti");
  a(ti, "checkIEEE754");
  function ri(r, e, t, n, i) {
    return e = +e, t = t >>> 0, i || ti(r, e, t, 4, 34028234663852886e22, -34028234663852886e22), Re.write(r, e, t, n, 23, 4), t + 4;
  }
  __name(ri, "ri");
  a(
    ri,
    "writeFloat"
  );
  d.prototype.writeFloatLE = a(function(e, t, n) {
    return ri(this, e, t, true, n);
  }, "writeFloatLE");
  d.prototype.writeFloatBE = a(function(e, t, n) {
    return ri(this, e, t, false, n);
  }, "writeFloatBE");
  function ni(r, e, t, n, i) {
    return e = +e, t = t >>> 0, i || ti(r, e, t, 8, 17976931348623157e292, -17976931348623157e292), Re.write(
      r,
      e,
      t,
      n,
      52,
      8
    ), t + 8;
  }
  __name(ni, "ni");
  a(ni, "writeDouble");
  d.prototype.writeDoubleLE = a(function(e, t, n) {
    return ni(this, e, t, true, n);
  }, "writeDoubleLE");
  d.prototype.writeDoubleBE = a(function(e, t, n) {
    return ni(this, e, t, false, n);
  }, "writeDoubleBE");
  d.prototype.copy = a(function(e, t, n, i) {
    if (!d.isBuffer(e)) throw new TypeError("argument should be a Buffer");
    if (n || (n = 0), !i && i !== 0 && (i = this.length), t >= e.length && (t = e.length), t || (t = 0), i > 0 && i < n && (i = n), i === n || e.length === 0 || this.length === 0) return 0;
    if (t < 0) throw new RangeError("targetStart out of bounds");
    if (n < 0 || n >= this.length) throw new RangeError("Index out of range");
    if (i < 0) throw new RangeError("sourceEnd out of bounds");
    i > this.length && (i = this.length), e.length - t < i - n && (i = e.length - t + n);
    let s = i - n;
    return this === e && typeof Uint8Array.prototype.copyWithin == "function" ? this.copyWithin(t, n, i) : Uint8Array.prototype.set.call(e, this.subarray(n, i), t), s;
  }, "copy");
  d.prototype.fill = a(function(e, t, n, i) {
    if (typeof e == "string") {
      if (typeof t == "string" ? (i = t, t = 0, n = this.length) : typeof n == "string" && (i = n, n = this.length), i !== void 0 && typeof i != "string") throw new TypeError("encoding must be a string");
      if (typeof i == "string" && !d.isEncoding(i)) throw new TypeError(
        "Unknown encoding: " + i
      );
      if (e.length === 1) {
        let o = e.charCodeAt(0);
        (i === "utf8" && o < 128 || i === "latin1") && (e = o);
      }
    } else typeof e == "number" ? e = e & 255 : typeof e == "boolean" && (e = Number(e));
    if (t < 0 || this.length < t || this.length < n) throw new RangeError("Out of range index");
    if (n <= t) return this;
    t = t >>> 0, n = n === void 0 ? this.length : n >>> 0, e || (e = 0);
    let s;
    if (typeof e == "number") for (s = t; s < n; ++s) this[s] = e;
    else {
      let o = d.isBuffer(e) ? e : d.from(
        e,
        i
      ), u = o.length;
      if (u === 0) throw new TypeError('The value "' + e + '" is invalid for argument "value"');
      for (s = 0; s < n - t; ++s) this[s + t] = o[s % u];
    }
    return this;
  }, "fill");
  var Pe = {};
  function zt(r, e, t) {
    var n;
    Pe[r] = (n = class extends t {
      static {
        __name(this, "n");
      }
      constructor() {
        super(), Object.defineProperty(this, "message", { value: e.apply(this, arguments), writable: true, configurable: true }), this.name = `${this.name} [${r}]`, this.stack, delete this.name;
      }
      get code() {
        return r;
      }
      set code(s) {
        Object.defineProperty(
          this,
          "code",
          { configurable: true, enumerable: true, value: s, writable: true }
        );
      }
      toString() {
        return `${this.name} [${r}]: ${this.message}`;
      }
    }, a(n, "NodeError"), n);
  }
  __name(zt, "zt");
  a(zt, "E");
  zt("ERR_BUFFER_OUT_OF_BOUNDS", function(r) {
    return r ? `${r} is outside of buffer bounds` : "Attempt to access memory outside buffer bounds";
  }, RangeError);
  zt(
    "ERR_INVALID_ARG_TYPE",
    function(r, e) {
      return `The "${r}" argument must be of type number. Received type ${typeof e}`;
    },
    TypeError
  );
  zt("ERR_OUT_OF_RANGE", function(r, e, t) {
    let n = `The value of "${r}" is out of range.`, i = t;
    return Number.isInteger(t) && Math.abs(t) > 2 ** 32 ? i = Vn(String(t)) : typeof t == "bigint" && (i = String(
      t
    ), (t > BigInt(2) ** BigInt(32) || t < -(BigInt(2) ** BigInt(32))) && (i = Vn(i)), i += "n"), n += ` It must be ${e}. Received ${i}`, n;
  }, RangeError);
  function Vn(r) {
    let e = "", t = r.length, n = r[0] === "-" ? 1 : 0;
    for (; t >= n + 4; t -= 3) e = `_${r.slice(t - 3, t)}${e}`;
    return `${r.slice(0, t)}${e}`;
  }
  __name(Vn, "Vn");
  a(Vn, "addNumericalSeparator");
  function oa(r, e, t) {
    Le(e, "offset"), (r[e] === void 0 || r[e + t] === void 0) && We(e, r.length - (t + 1));
  }
  __name(oa, "oa");
  a(oa, "checkBounds");
  function ii(r, e, t, n, i, s) {
    if (r > t || r < e) {
      let o = typeof e == "bigint" ? "n" : "", u;
      throw s > 3 ? e === 0 || e === BigInt(0) ? u = `>= 0${o} and < 2${o} ** ${(s + 1) * 8}${o}` : u = `>= -(2${o} ** ${(s + 1) * 8 - 1}${o}) and < 2 ** ${(s + 1) * 8 - 1}${o}` : u = `>= ${e}${o} and <= ${t}${o}`, new Pe.ERR_OUT_OF_RANGE("value", u, r);
    }
    oa(n, i, s);
  }
  __name(ii, "ii");
  a(ii, "checkIntBI");
  function Le(r, e) {
    if (typeof r != "number") throw new Pe.ERR_INVALID_ARG_TYPE(e, "number", r);
  }
  __name(Le, "Le");
  a(Le, "validateNumber");
  function We(r, e, t) {
    throw Math.floor(r) !== r ? (Le(r, t), new Pe.ERR_OUT_OF_RANGE(t || "offset", "an integer", r)) : e < 0 ? new Pe.ERR_BUFFER_OUT_OF_BOUNDS() : new Pe.ERR_OUT_OF_RANGE(t || "offset", `>= ${t ? 1 : 0} and <= ${e}`, r);
  }
  __name(We, "We");
  a(We, "boundsError");
  var aa = /[^+/0-9A-Za-z-_]/g;
  function ua(r) {
    if (r = r.split("=")[0], r = r.trim().replace(aa, ""), r.length < 2) return "";
    for (; r.length % 4 !== 0; ) r = r + "=";
    return r;
  }
  __name(ua, "ua");
  a(ua, "base64clean");
  function $t(r, e) {
    e = e || 1 / 0;
    let t, n = r.length, i = null, s = [];
    for (let o = 0; o < n; ++o) {
      if (t = r.charCodeAt(o), t > 55295 && t < 57344) {
        if (!i) {
          if (t > 56319) {
            (e -= 3) > -1 && s.push(239, 191, 189);
            continue;
          } else if (o + 1 === n) {
            (e -= 3) > -1 && s.push(239, 191, 189);
            continue;
          }
          i = t;
          continue;
        }
        if (t < 56320) {
          (e -= 3) > -1 && s.push(239, 191, 189), i = t;
          continue;
        }
        t = (i - 55296 << 10 | t - 56320) + 65536;
      } else i && (e -= 3) > -1 && s.push(239, 191, 189);
      if (i = null, t < 128) {
        if ((e -= 1) < 0) break;
        s.push(t);
      } else if (t < 2048) {
        if ((e -= 2) < 0) break;
        s.push(t >> 6 | 192, t & 63 | 128);
      } else if (t < 65536) {
        if ((e -= 3) < 0) break;
        s.push(t >> 12 | 224, t >> 6 & 63 | 128, t & 63 | 128);
      } else if (t < 1114112) {
        if ((e -= 4) < 0) break;
        s.push(t >> 18 | 240, t >> 12 & 63 | 128, t >> 6 & 63 | 128, t & 63 | 128);
      } else throw new Error("Invalid code point");
    }
    return s;
  }
  __name($t, "$t");
  a($t, "utf8ToBytes");
  function ca(r) {
    let e = [];
    for (let t = 0; t < r.length; ++t) e.push(r.charCodeAt(t) & 255);
    return e;
  }
  __name(ca, "ca");
  a(
    ca,
    "asciiToBytes"
  );
  function la(r, e) {
    let t, n, i, s = [];
    for (let o = 0; o < r.length && !((e -= 2) < 0); ++o) t = r.charCodeAt(
      o
    ), n = t >> 8, i = t % 256, s.push(i), s.push(n);
    return s;
  }
  __name(la, "la");
  a(la, "utf16leToBytes");
  function si(r) {
    return Wt.toByteArray(
      ua(r)
    );
  }
  __name(si, "si");
  a(si, "base64ToBytes");
  function ht(r, e, t, n) {
    let i;
    for (i = 0; i < n && !(i + t >= e.length || i >= r.length); ++i)
      e[i + t] = r[i];
    return i;
  }
  __name(ht, "ht");
  a(ht, "blitBuffer");
  function fe(r, e) {
    return r instanceof e || r != null && r.constructor != null && r.constructor.name != null && r.constructor.name === e.name;
  }
  __name(fe, "fe");
  a(fe, "isInstance");
  function Kt(r) {
    return r !== r;
  }
  __name(Kt, "Kt");
  a(Kt, "numberIsNaN");
  var fa = (function() {
    let r = "0123456789abcdef", e = new Array(256);
    for (let t = 0; t < 16; ++t) {
      let n = t * 16;
      for (let i = 0; i < 16; ++i) e[n + i] = r[t] + r[i];
    }
    return e;
  })();
  function be(r) {
    return typeof BigInt > "u" ? ha : r;
  }
  __name(be, "be");
  a(be, "defineBigIntMethod");
  function ha() {
    throw new Error("BigInt not supported");
  }
  __name(ha, "ha");
  a(ha, "BufferBigIntNotDefined");
});
var b;
var x;
var v;
var p;
var y;
var h = V(() => {
  "use strict";
  b = globalThis, x = globalThis.setImmediate ?? ((r) => setTimeout(r, 0)), v = globalThis.clearImmediate ?? ((r) => clearTimeout(r)), p = typeof globalThis.Buffer == "function" && typeof globalThis.Buffer.allocUnsafe == "function" ? globalThis.Buffer : oi().Buffer, y = globalThis.process ?? {};
  y.env ?? (y.env = {});
  try {
    y.nextTick(() => {
    });
  } catch {
    let e = Promise.resolve();
    y.nextTick = e.then.bind(e);
  }
});
var ve = T((Ef, Xt) => {
  "use strict";
  h();
  var Fe = typeof Reflect == "object" ? Reflect : null, mi = Fe && typeof Fe.apply == "function" ? Fe.apply : a(function(e, t, n) {
    return Function.prototype.apply.call(e, t, n);
  }, "ReflectApply"), bt;
  Fe && typeof Fe.ownKeys == "function" ? bt = Fe.ownKeys : Object.getOwnPropertySymbols ? bt = a(function(e) {
    return Object.getOwnPropertyNames(e).concat(Object.getOwnPropertySymbols(e));
  }, "ReflectOwnKeys") : bt = a(function(e) {
    return Object.getOwnPropertyNames(e);
  }, "ReflectOwnKeys");
  function Ia(r) {
    console && console.warn && console.warn(r);
  }
  __name(Ia, "Ia");
  a(
    Ia,
    "ProcessEmitWarning"
  );
  var wi = Number.isNaN || a(function(e) {
    return e !== e;
  }, "NumberIsNaN");
  function P() {
    P.init.call(this);
  }
  __name(P, "P");
  a(P, "EventEmitter");
  Xt.exports = P;
  Xt.exports.once = Ba;
  P.EventEmitter = P;
  P.prototype._events = void 0;
  P.prototype._eventsCount = 0;
  P.prototype._maxListeners = void 0;
  var gi = 10;
  function xt(r) {
    if (typeof r != "function") throw new TypeError('The "listener" argument must be of type Function. Received type ' + typeof r);
  }
  __name(xt, "xt");
  a(xt, "checkListener");
  Object.defineProperty(P, "defaultMaxListeners", { enumerable: true, get: a(function() {
    return gi;
  }, "get"), set: a(
    function(r) {
      if (typeof r != "number" || r < 0 || wi(r)) throw new RangeError('The value of "defaultMaxListeners" is out of range. It must be a non-negative number. Received ' + r + ".");
      gi = r;
    },
    "set"
  ) });
  P.init = function() {
    (this._events === void 0 || this._events === Object.getPrototypeOf(this)._events) && (this._events = /* @__PURE__ */ Object.create(null), this._eventsCount = 0), this._maxListeners = this._maxListeners || void 0;
  };
  P.prototype.setMaxListeners = a(function(e) {
    if (typeof e != "number" || e < 0 || wi(e)) throw new RangeError('The value of "n" is out of range. It must be a non-negative number. Received ' + e + ".");
    return this._maxListeners = e, this;
  }, "setMaxListeners");
  function bi(r) {
    return r._maxListeners === void 0 ? P.defaultMaxListeners : r._maxListeners;
  }
  __name(bi, "bi");
  a(bi, "_getMaxListeners");
  P.prototype.getMaxListeners = a(function() {
    return bi(this);
  }, "getMaxListeners");
  P.prototype.emit = a(function(e) {
    for (var t = [], n = 1; n < arguments.length; n++) t.push(arguments[n]);
    var i = e === "error", s = this._events;
    if (s !== void 0) i = i && s.error === void 0;
    else if (!i) return false;
    if (i) {
      var o;
      if (t.length > 0 && (o = t[0]), o instanceof Error) throw o;
      var u = new Error("Unhandled error." + (o ? " (" + o.message + ")" : ""));
      throw u.context = o, u;
    }
    var c = s[e];
    if (c === void 0) return false;
    if (typeof c == "function") mi(c, this, t);
    else for (var l = c.length, f = Ai(c, l), n = 0; n < l; ++n) mi(f[n], this, t);
    return true;
  }, "emit");
  function xi(r, e, t, n) {
    var i, s, o;
    if (xt(
      t
    ), s = r._events, s === void 0 ? (s = r._events = /* @__PURE__ */ Object.create(null), r._eventsCount = 0) : (s.newListener !== void 0 && (r.emit("newListener", e, t.listener ? t.listener : t), s = r._events), o = s[e]), o === void 0) o = s[e] = t, ++r._eventsCount;
    else if (typeof o == "function" ? o = s[e] = n ? [t, o] : [o, t] : n ? o.unshift(t) : o.push(t), i = bi(r), i > 0 && o.length > i && !o.warned) {
      o.warned = true;
      var u = new Error("Possible EventEmitter memory leak detected. " + o.length + " " + String(e) + " listeners added. Use emitter.setMaxListeners() to increase limit");
      u.name = "MaxListenersExceededWarning", u.emitter = r, u.type = e, u.count = o.length, Ia(u);
    }
    return r;
  }
  __name(xi, "xi");
  a(xi, "_addListener");
  P.prototype.addListener = a(function(e, t) {
    return xi(this, e, t, false);
  }, "addListener");
  P.prototype.on = P.prototype.addListener;
  P.prototype.prependListener = a(function(e, t) {
    return xi(this, e, t, true);
  }, "prependListener");
  function Pa() {
    if (!this.fired) return this.target.removeListener(this.type, this.wrapFn), this.fired = true, arguments.length === 0 ? this.listener.call(this.target) : this.listener.apply(this.target, arguments);
  }
  __name(Pa, "Pa");
  a(Pa, "onceWrapper");
  function vi(r, e, t) {
    var n = {
      fired: false,
      wrapFn: void 0,
      target: r,
      type: e,
      listener: t
    }, i = Pa.bind(n);
    return i.listener = t, n.wrapFn = i, i;
  }
  __name(vi, "vi");
  a(vi, "_onceWrap");
  P.prototype.once = a(function(e, t) {
    return xt(t), this.on(e, vi(this, e, t)), this;
  }, "once");
  P.prototype.prependOnceListener = a(function(e, t) {
    return xt(t), this.prependListener(e, vi(this, e, t)), this;
  }, "prependOnceListener");
  P.prototype.removeListener = a(function(e, t) {
    var n, i, s, o, u;
    if (xt(t), i = this._events, i === void 0) return this;
    if (n = i[e], n === void 0) return this;
    if (n === t || n.listener === t) --this._eventsCount === 0 ? this._events = /* @__PURE__ */ Object.create(null) : (delete i[e], i.removeListener && this.emit("removeListener", e, n.listener || t));
    else if (typeof n != "function") {
      for (s = -1, o = n.length - 1; o >= 0; o--) if (n[o] === t || n[o].listener === t) {
        u = n[o].listener, s = o;
        break;
      }
      if (s < 0) return this;
      s === 0 ? n.shift() : Ra(n, s), n.length === 1 && (i[e] = n[0]), i.removeListener !== void 0 && this.emit("removeListener", e, u || t);
    }
    return this;
  }, "removeListener");
  P.prototype.off = P.prototype.removeListener;
  P.prototype.removeAllListeners = a(function(e) {
    var t, n, i;
    if (n = this._events, n === void 0) return this;
    if (n.removeListener === void 0) return arguments.length === 0 ? (this._events = /* @__PURE__ */ Object.create(null), this._eventsCount = 0) : n[e] !== void 0 && (--this._eventsCount === 0 ? this._events = /* @__PURE__ */ Object.create(null) : delete n[e]), this;
    if (arguments.length === 0) {
      var s = Object.keys(n), o;
      for (i = 0; i < s.length; ++i) o = s[i], o !== "removeListener" && this.removeAllListeners(
        o
      );
      return this.removeAllListeners("removeListener"), this._events = /* @__PURE__ */ Object.create(null), this._eventsCount = 0, this;
    }
    if (t = n[e], typeof t == "function") this.removeListener(e, t);
    else if (t !== void 0) for (i = t.length - 1; i >= 0; i--) this.removeListener(e, t[i]);
    return this;
  }, "removeAllListeners");
  function Si(r, e, t) {
    var n = r._events;
    if (n === void 0) return [];
    var i = n[e];
    return i === void 0 ? [] : typeof i == "function" ? t ? [i.listener || i] : [i] : t ? La(i) : Ai(i, i.length);
  }
  __name(Si, "Si");
  a(Si, "_listeners");
  P.prototype.listeners = a(function(e) {
    return Si(this, e, true);
  }, "listeners");
  P.prototype.rawListeners = a(function(e) {
    return Si(this, e, false);
  }, "rawListeners");
  P.listenerCount = function(r, e) {
    return typeof r.listenerCount == "function" ? r.listenerCount(e) : Ei.call(r, e);
  };
  P.prototype.listenerCount = Ei;
  function Ei(r) {
    var e = this._events;
    if (e !== void 0) {
      var t = e[r];
      if (typeof t == "function")
        return 1;
      if (t !== void 0) return t.length;
    }
    return 0;
  }
  __name(Ei, "Ei");
  a(Ei, "listenerCount");
  P.prototype.eventNames = a(function() {
    return this._eventsCount > 0 ? bt(this._events) : [];
  }, "eventNames");
  function Ai(r, e) {
    for (var t = new Array(e), n = 0; n < e; ++n) t[n] = r[n];
    return t;
  }
  __name(Ai, "Ai");
  a(Ai, "arrayClone");
  function Ra(r, e) {
    for (; e + 1 < r.length; e++) r[e] = r[e + 1];
    r.pop();
  }
  __name(Ra, "Ra");
  a(Ra, "spliceOne");
  function La(r) {
    for (var e = new Array(r.length), t = 0; t < e.length; ++t) e[t] = r[t].listener || r[t];
    return e;
  }
  __name(La, "La");
  a(La, "unwrapListeners");
  function Ba(r, e) {
    return new Promise(function(t, n) {
      function i(o) {
        r.removeListener(e, s), n(o);
      }
      __name(i, "i");
      a(i, "errorListener");
      function s() {
        typeof r.removeListener == "function" && r.removeListener("error", i), t([].slice.call(arguments));
      }
      __name(s, "s");
      a(s, "resolver"), Ci(r, e, s, { once: true }), e !== "error" && Fa(r, i, { once: true });
    });
  }
  __name(Ba, "Ba");
  a(Ba, "once");
  function Fa(r, e, t) {
    typeof r.on == "function" && Ci(r, "error", e, t);
  }
  __name(Fa, "Fa");
  a(
    Fa,
    "addErrorHandlerIfEventEmitter"
  );
  function Ci(r, e, t, n) {
    if (typeof r.on == "function") n.once ? r.once(e, t) : r.on(e, t);
    else if (typeof r.addEventListener == "function") r.addEventListener(e, a(/* @__PURE__ */ __name(function i(s) {
      n.once && r.removeEventListener(e, i), t(s);
    }, "i"), "wrapListener"));
    else throw new TypeError('The "emitter" argument must be of type EventEmitter. Received type ' + typeof r);
  }
  __name(Ci, "Ci");
  a(Ci, "eventTargetAgnosticAddListener");
});
var Ii = {};
se(Ii, { Socket: /* @__PURE__ */ __name(() => pe, "Socket"), isIP: /* @__PURE__ */ __name(() => Ma, "isIP") });
function Ma(r) {
  return 0;
}
__name(Ma, "Ma");
var Ti;
var _i;
var A;
var pe;
var Ge = V(() => {
  "use strict";
  h();
  Ti = we(ve(), 1);
  a(Ma, "isIP");
  _i = /^[^.]+\./, A = class A2 extends Ti.EventEmitter {
    static {
      __name(this, "A");
    }
    constructor() {
      super(...arguments);
      E(this, "opts", {});
      E(this, "connecting", false);
      E(this, "pending", true);
      E(
        this,
        "writable",
        true
      );
      E(this, "encrypted", false);
      E(this, "authorized", false);
      E(this, "destroyed", false);
      E(this, "ws", null);
      E(this, "writeBuffer");
      E(this, "tlsState", 0);
      E(this, "tlsRead");
      E(this, "tlsWrite");
    }
    static get poolQueryViaFetch() {
      return A2.opts.poolQueryViaFetch ?? A2.defaults.poolQueryViaFetch;
    }
    static set poolQueryViaFetch(t) {
      A2.opts.poolQueryViaFetch = t;
    }
    static get fetchEndpoint() {
      return A2.opts.fetchEndpoint ?? A2.defaults.fetchEndpoint;
    }
    static set fetchEndpoint(t) {
      A2.opts.fetchEndpoint = t;
    }
    static get fetchConnectionCache() {
      return true;
    }
    static set fetchConnectionCache(t) {
      console.warn("The `fetchConnectionCache` option is deprecated (now always `true`)");
    }
    static get fetchFunction() {
      return A2.opts.fetchFunction ?? A2.defaults.fetchFunction;
    }
    static set fetchFunction(t) {
      A2.opts.fetchFunction = t;
    }
    static get webSocketConstructor() {
      return A2.opts.webSocketConstructor ?? A2.defaults.webSocketConstructor;
    }
    static set webSocketConstructor(t) {
      A2.opts.webSocketConstructor = t;
    }
    get webSocketConstructor() {
      return this.opts.webSocketConstructor ?? A2.webSocketConstructor;
    }
    set webSocketConstructor(t) {
      this.opts.webSocketConstructor = t;
    }
    static get wsProxy() {
      return A2.opts.wsProxy ?? A2.defaults.wsProxy;
    }
    static set wsProxy(t) {
      A2.opts.wsProxy = t;
    }
    get wsProxy() {
      return this.opts.wsProxy ?? A2.wsProxy;
    }
    set wsProxy(t) {
      this.opts.wsProxy = t;
    }
    static get coalesceWrites() {
      return A2.opts.coalesceWrites ?? A2.defaults.coalesceWrites;
    }
    static set coalesceWrites(t) {
      A2.opts.coalesceWrites = t;
    }
    get coalesceWrites() {
      return this.opts.coalesceWrites ?? A2.coalesceWrites;
    }
    set coalesceWrites(t) {
      this.opts.coalesceWrites = t;
    }
    static get useSecureWebSocket() {
      return A2.opts.useSecureWebSocket ?? A2.defaults.useSecureWebSocket;
    }
    static set useSecureWebSocket(t) {
      A2.opts.useSecureWebSocket = t;
    }
    get useSecureWebSocket() {
      return this.opts.useSecureWebSocket ?? A2.useSecureWebSocket;
    }
    set useSecureWebSocket(t) {
      this.opts.useSecureWebSocket = t;
    }
    static get forceDisablePgSSL() {
      return A2.opts.forceDisablePgSSL ?? A2.defaults.forceDisablePgSSL;
    }
    static set forceDisablePgSSL(t) {
      A2.opts.forceDisablePgSSL = t;
    }
    get forceDisablePgSSL() {
      return this.opts.forceDisablePgSSL ?? A2.forceDisablePgSSL;
    }
    set forceDisablePgSSL(t) {
      this.opts.forceDisablePgSSL = t;
    }
    static get disableSNI() {
      return A2.opts.disableSNI ?? A2.defaults.disableSNI;
    }
    static set disableSNI(t) {
      A2.opts.disableSNI = t;
    }
    get disableSNI() {
      return this.opts.disableSNI ?? A2.disableSNI;
    }
    set disableSNI(t) {
      this.opts.disableSNI = t;
    }
    static get disableWarningInBrowsers() {
      return A2.opts.disableWarningInBrowsers ?? A2.defaults.disableWarningInBrowsers;
    }
    static set disableWarningInBrowsers(t) {
      A2.opts.disableWarningInBrowsers = t;
    }
    get disableWarningInBrowsers() {
      return this.opts.disableWarningInBrowsers ?? A2.disableWarningInBrowsers;
    }
    set disableWarningInBrowsers(t) {
      this.opts.disableWarningInBrowsers = t;
    }
    static get pipelineConnect() {
      return A2.opts.pipelineConnect ?? A2.defaults.pipelineConnect;
    }
    static set pipelineConnect(t) {
      A2.opts.pipelineConnect = t;
    }
    get pipelineConnect() {
      return this.opts.pipelineConnect ?? A2.pipelineConnect;
    }
    set pipelineConnect(t) {
      this.opts.pipelineConnect = t;
    }
    static get subtls() {
      return A2.opts.subtls ?? A2.defaults.subtls;
    }
    static set subtls(t) {
      A2.opts.subtls = t;
    }
    get subtls() {
      return this.opts.subtls ?? A2.subtls;
    }
    set subtls(t) {
      this.opts.subtls = t;
    }
    static get pipelineTLS() {
      return A2.opts.pipelineTLS ?? A2.defaults.pipelineTLS;
    }
    static set pipelineTLS(t) {
      A2.opts.pipelineTLS = t;
    }
    get pipelineTLS() {
      return this.opts.pipelineTLS ?? A2.pipelineTLS;
    }
    set pipelineTLS(t) {
      this.opts.pipelineTLS = t;
    }
    static get rootCerts() {
      return A2.opts.rootCerts ?? A2.defaults.rootCerts;
    }
    static set rootCerts(t) {
      A2.opts.rootCerts = t;
    }
    get rootCerts() {
      return this.opts.rootCerts ?? A2.rootCerts;
    }
    set rootCerts(t) {
      this.opts.rootCerts = t;
    }
    wsProxyAddrForHost(t, n) {
      let i = this.wsProxy;
      if (i === void 0) throw new Error("No WebSocket proxy is configured. Please see https://github.com/neondatabase/serverless/blob/main/CONFIG.md#wsproxy-string--host-string-port-number--string--string");
      return typeof i == "function" ? i(t, n) : `${i}?address=${t}:${n}`;
    }
    setNoDelay() {
      return this;
    }
    setKeepAlive() {
      return this;
    }
    ref() {
      return this;
    }
    unref() {
      return this;
    }
    connect(t, n, i) {
      this.connecting = true, i && this.once("connect", i);
      let s = a(() => {
        this.connecting = false, this.pending = false, this.emit("connect"), this.emit("ready");
      }, "handleWebSocketOpen"), o = a((c, l = false) => {
        c.binaryType = "arraybuffer", c.addEventListener("error", (f) => {
          this.emit("error", f), this.emit("close");
        }), c.addEventListener("message", (f) => {
          if (this.tlsState === 0) {
            let m = p.from(f.data);
            this.emit("data", m);
          }
        }), c.addEventListener("close", () => {
          this.destroyed = true, this.emit("close");
        }), l ? s() : c.addEventListener("open", s);
      }, "configureWebSocket"), u;
      try {
        u = this.wsProxyAddrForHost(n, typeof t == "string" ? parseInt(t, 10) : t);
      } catch (c) {
        this.emit("error", c), this.emit("close");
        return;
      }
      try {
        let l = (this.useSecureWebSocket ? "wss:" : "ws:") + "//" + u;
        if (this.webSocketConstructor !== void 0) this.ws = new this.webSocketConstructor(l), o(this.ws);
        else try {
          this.ws = new WebSocket(l), o(this.ws);
        } catch {
          this.ws = new __unstable_WebSocket(l), o(
            this.ws
          );
        }
      } catch (c) {
        let f = (this.useSecureWebSocket ? "https:" : "http:") + "//" + u;
        fetch(f, { headers: { Upgrade: "websocket" } }).then((m) => {
          if (this.ws = m.webSocket, this.ws == null) throw c;
          this.ws.accept(), o(this.ws, true);
        }).catch((m) => {
          this.emit("error", new Error(`All attempts to open a WebSocket to connect to the database failed. Please refer to https://github.com/neondatabase/serverless/blob/main/CONFIG.md#websocketconstructor-typeof-websocket--undefined. Details: ${m}`)), this.emit("close");
        });
      }
    }
    async startTls(t) {
      if (this.subtls === void 0) throw new Error("For Postgres SSL connections, you must set `neonConfig.subtls` to the subtls library. See https://github.com/neondatabase/serverless/blob/main/CONFIG.md for more information.");
      this.tlsState = 1;
      let n = await this.subtls.TrustedCert.databaseFromPEM(this.rootCerts), i = new this.subtls.WebSocketReadQueue(this.ws), s = i.read.bind(i), o = this.rawWrite.bind(this), { read: u, write: c } = await this.subtls.startTls(t, n, s, o, { useSNI: !this.disableSNI, expectPreData: this.pipelineTLS ? new Uint8Array([83]) : void 0 });
      this.tlsRead = u, this.tlsWrite = c, this.tlsState = 2, this.encrypted = true, this.authorized = true, this.emit(
        "secureConnection",
        this
      ), this.tlsReadLoop().catch((l) => {
        this.destroyed || (this.destroyed = true, this.emit("error", l), this.ws?.close());
      });
    }
    async tlsReadLoop() {
      for (; ; ) {
        let t = await this.tlsRead();
        if (t === void 0) break;
        {
          let n = p.from(t);
          this.emit("data", n);
        }
      }
    }
    rawWrite(t) {
      if (!this.coalesceWrites) {
        this.ws && this.ws.send(t);
        return;
      }
      if (this.writeBuffer === void 0) this.writeBuffer = t, setTimeout(() => {
        this.ws && this.ws.send(this.writeBuffer), this.writeBuffer = void 0;
      }, 0);
      else {
        let n = new Uint8Array(this.writeBuffer.length + t.length);
        n.set(this.writeBuffer), n.set(t, this.writeBuffer.length), this.writeBuffer = n;
      }
    }
    write(t, n = "utf8", i = (s) => {
    }) {
      return t.length === 0 ? (i(), true) : (typeof t == "string" && (t = p.from(t, n)), this.tlsState === 0 ? (this.rawWrite(t), i()) : this.tlsState === 1 ? this.once("secureConnection", () => {
        this.write(t, n, i);
      }) : (this.tlsWrite(t), i()), true);
    }
    end(t = p.alloc(0), n = "utf8", i = () => {
    }) {
      return this.write(t, n, () => {
        this.ws?.close(), i();
      }), this;
    }
    destroy() {
      return this.destroyed = true, this.end();
    }
  };
  a(A, "Socket"), E(A, "defaults", {
    poolQueryViaFetch: false,
    fetchEndpoint: a((t, n, i) => {
      let s;
      return i?.jwtAuth ? s = t.replace(_i, "apiauth.") : s = t.replace(_i, "api."), "https://" + s + "/sql";
    }, "fetchEndpoint"),
    fetchConnectionCache: true,
    fetchFunction: void 0,
    webSocketConstructor: void 0,
    wsProxy: a((t) => t + "/v2", "wsProxy"),
    useSecureWebSocket: true,
    forceDisablePgSSL: true,
    coalesceWrites: true,
    pipelineConnect: "password",
    subtls: void 0,
    rootCerts: "",
    pipelineTLS: false,
    disableSNI: false,
    disableWarningInBrowsers: false
  }), E(A, "opts", {});
  pe = A;
});
var tr = T((Pi) => {
  "use strict";
  h();
  Pi.parse = function(r, e) {
    return new er(r, e).parse();
  };
  var St = class St2 {
    static {
      __name(this, "St");
    }
    constructor(e, t) {
      this.source = e, this.transform = t || ka, this.position = 0, this.entries = [], this.recorded = [], this.dimension = 0;
    }
    isEof() {
      return this.position >= this.source.length;
    }
    nextCharacter() {
      var e = this.source[this.position++];
      return e === "\\" ? { value: this.source[this.position++], escaped: true } : { value: e, escaped: false };
    }
    record(e) {
      this.recorded.push(
        e
      );
    }
    newEntry(e) {
      var t;
      (this.recorded.length > 0 || e) && (t = this.recorded.join(""), t === "NULL" && !e && (t = null), t !== null && (t = this.transform(t)), this.entries.push(t), this.recorded = []);
    }
    consumeDimensions() {
      if (this.source[0] === "[") for (; !this.isEof(); ) {
        var e = this.nextCharacter();
        if (e.value === "=") break;
      }
    }
    parse(e) {
      var t, n, i;
      for (this.consumeDimensions(); !this.isEof(); ) if (t = this.nextCharacter(), t.value === "{" && !i) this.dimension++, this.dimension > 1 && (n = new St2(this.source.substr(this.position - 1), this.transform), this.entries.push(n.parse(
        true
      )), this.position += n.position - 2);
      else if (t.value === "}" && !i) {
        if (this.dimension--, !this.dimension && (this.newEntry(), e)) return this.entries;
      } else t.value === '"' && !t.escaped ? (i && this.newEntry(true), i = !i) : t.value === "," && !i ? this.newEntry() : this.record(t.value);
      if (this.dimension !== 0) throw new Error("array dimension not balanced");
      return this.entries;
    }
  };
  a(St, "ArrayParser");
  var er = St;
  function ka(r) {
    return r;
  }
  __name(ka, "ka");
  a(ka, "identity");
});
var rr = T((Ff, Ri) => {
  h();
  var Oa = tr();
  Ri.exports = { create: a(function(r, e) {
    return { parse: a(function() {
      return Oa.parse(r, e);
    }, "parse") };
  }, "create") };
});
var Fi = T((Of, Bi) => {
  "use strict";
  h();
  var Ua = /(\d{1,})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})(\.\d{1,})?.*?( BC)?$/, Qa = /^(\d{1,})-(\d{2})-(\d{2})( BC)?$/, Da = /([Z+-])(\d{2})?:?(\d{2})?:?(\d{2})?/, qa = /^-?infinity$/;
  Bi.exports = a(function(e) {
    if (qa.test(e)) return Number(e.replace("i", "I"));
    var t = Ua.exec(e);
    if (!t) return Na(
      e
    ) || null;
    var n = !!t[8], i = parseInt(t[1], 10);
    n && (i = Li(i));
    var s = parseInt(t[2], 10) - 1, o = t[3], u = parseInt(
      t[4],
      10
    ), c = parseInt(t[5], 10), l = parseInt(t[6], 10), f = t[7];
    f = f ? 1e3 * parseFloat(f) : 0;
    var m, g = Wa(e);
    return g != null ? (m = new Date(Date.UTC(i, s, o, u, c, l, f)), nr(i) && m.setUTCFullYear(i), g !== 0 && m.setTime(m.getTime() - g)) : (m = new Date(i, s, o, u, c, l, f), nr(i) && m.setFullYear(i)), m;
  }, "parseDate");
  function Na(r) {
    var e = Qa.exec(r);
    if (e) {
      var t = parseInt(e[1], 10), n = !!e[4];
      n && (t = Li(t));
      var i = parseInt(e[2], 10) - 1, s = e[3], o = new Date(t, i, s);
      return nr(
        t
      ) && o.setFullYear(t), o;
    }
  }
  __name(Na, "Na");
  a(Na, "getDate");
  function Wa(r) {
    if (r.endsWith("+00")) return 0;
    var e = Da.exec(r.split(" ")[1]);
    if (e) {
      var t = e[1];
      if (t === "Z") return 0;
      var n = t === "-" ? -1 : 1, i = parseInt(e[2], 10) * 3600 + parseInt(
        e[3] || 0,
        10
      ) * 60 + parseInt(e[4] || 0, 10);
      return i * n * 1e3;
    }
  }
  __name(Wa, "Wa");
  a(Wa, "timeZoneOffset");
  function Li(r) {
    return -(r - 1);
  }
  __name(Li, "Li");
  a(Li, "bcYearToNegativeYear");
  function nr(r) {
    return r >= 0 && r < 100;
  }
  __name(nr, "nr");
  a(nr, "is0To99");
});
var ki = T((Df, Mi) => {
  h();
  Mi.exports = Ha;
  var ja = Object.prototype.hasOwnProperty;
  function Ha(r) {
    for (var e = 1; e < arguments.length; e++) {
      var t = arguments[e];
      for (var n in t) ja.call(t, n) && (r[n] = t[n]);
    }
    return r;
  }
  __name(Ha, "Ha");
  a(Ha, "extend");
});
var Qi = T((Wf, Ui) => {
  "use strict";
  h();
  var $a = ki();
  Ui.exports = Me;
  function Me(r) {
    if (!(this instanceof Me))
      return new Me(r);
    $a(this, nu(r));
  }
  __name(Me, "Me");
  a(Me, "PostgresInterval");
  var Ga = [
    "seconds",
    "minutes",
    "hours",
    "days",
    "months",
    "years"
  ];
  Me.prototype.toPostgres = function() {
    var r = Ga.filter(this.hasOwnProperty, this);
    return this.milliseconds && r.indexOf("seconds") < 0 && r.push("seconds"), r.length === 0 ? "0" : r.map(function(e) {
      var t = this[e] || 0;
      return e === "seconds" && this.milliseconds && (t = (t + this.milliseconds / 1e3).toFixed(6).replace(
        /\.?0+$/,
        ""
      )), t + " " + e;
    }, this).join(" ");
  };
  var Va = { years: "Y", months: "M", days: "D", hours: "H", minutes: "M", seconds: "S" }, za = ["years", "months", "days"], Ka = ["hours", "minutes", "seconds"];
  Me.prototype.toISOString = Me.prototype.toISO = function() {
    var r = za.map(t, this).join(""), e = Ka.map(t, this).join("");
    return "P" + r + "T" + e;
    function t(n) {
      var i = this[n] || 0;
      return n === "seconds" && this.milliseconds && (i = (i + this.milliseconds / 1e3).toFixed(6).replace(
        /0+$/,
        ""
      )), i + Va[n];
    }
    __name(t, "t");
  };
  var ir = "([+-]?\\d+)", Ya = ir + "\\s+years?", Za = ir + "\\s+mons?", Ja = ir + "\\s+days?", Xa = "([+-])?([\\d]*):(\\d\\d):(\\d\\d)\\.?(\\d{1,6})?", eu = new RegExp([Ya, Za, Ja, Xa].map(function(r) {
    return "(" + r + ")?";
  }).join("\\s*")), Oi = { years: 2, months: 4, days: 6, hours: 9, minutes: 10, seconds: 11, milliseconds: 12 }, tu = ["hours", "minutes", "seconds", "milliseconds"];
  function ru(r) {
    var e = r + "000000".slice(r.length);
    return parseInt(
      e,
      10
    ) / 1e3;
  }
  __name(ru, "ru");
  a(ru, "parseMilliseconds");
  function nu(r) {
    if (!r) return {};
    var e = eu.exec(r), t = e[8] === "-";
    return Object.keys(Oi).reduce(function(n, i) {
      var s = Oi[i], o = e[s];
      return !o || (o = i === "milliseconds" ? ru(o) : parseInt(o, 10), !o) || (t && ~tu.indexOf(i) && (o *= -1), n[i] = o), n;
    }, {});
  }
  __name(nu, "nu");
  a(nu, "parse");
});
var Ni = T(($f, qi) => {
  "use strict";
  h();
  var Di = p.from || p;
  qi.exports = a(function(e) {
    if (/^\\x/.test(e)) return Di(
      e.substr(2),
      "hex"
    );
    for (var t = "", n = 0; n < e.length; ) if (e[n] !== "\\") t += e[n], ++n;
    else if (/[0-7]{3}/.test(e.substr(n + 1, 3))) t += String.fromCharCode(parseInt(e.substr(n + 1, 3), 8)), n += 4;
    else {
      for (var i = 1; n + i < e.length && e[n + i] === "\\"; ) i++;
      for (var s = 0; s < Math.floor(i / 2); ++s) t += "\\";
      n += Math.floor(i / 2) * 2;
    }
    return Di(t, "binary");
  }, "parseBytea");
});
var zi = T((zf, Vi) => {
  h();
  var Ve = tr(), ze = rr(), Et = Fi(), ji = Qi(), Hi = Ni();
  function At(r) {
    return a(function(t) {
      return t === null ? t : r(t);
    }, "nullAllowed");
  }
  __name(At, "At");
  a(At, "allowNull");
  function $i(r) {
    return r === null ? r : r === "TRUE" || r === "t" || r === "true" || r === "y" || r === "yes" || r === "on" || r === "1";
  }
  __name($i, "$i");
  a($i, "parseBool");
  function iu(r) {
    return r ? Ve.parse(r, $i) : null;
  }
  __name(iu, "iu");
  a(iu, "parseBoolArray");
  function su(r) {
    return parseInt(r, 10);
  }
  __name(su, "su");
  a(su, "parseBaseTenInt");
  function sr(r) {
    return r ? Ve.parse(r, At(su)) : null;
  }
  __name(sr, "sr");
  a(sr, "parseIntegerArray");
  function ou(r) {
    return r ? Ve.parse(r, At(function(e) {
      return Gi(e).trim();
    })) : null;
  }
  __name(ou, "ou");
  a(ou, "parseBigIntegerArray");
  var au = a(function(r) {
    if (!r) return null;
    var e = ze.create(r, function(t) {
      return t !== null && (t = cr(t)), t;
    });
    return e.parse();
  }, "parsePointArray"), or = a(function(r) {
    if (!r) return null;
    var e = ze.create(r, function(t) {
      return t !== null && (t = parseFloat(t)), t;
    });
    return e.parse();
  }, "parseFloatArray"), ee = a(function(r) {
    if (!r) return null;
    var e = ze.create(r);
    return e.parse();
  }, "parseStringArray"), ar = a(function(r) {
    if (!r) return null;
    var e = ze.create(
      r,
      function(t) {
        return t !== null && (t = Et(t)), t;
      }
    );
    return e.parse();
  }, "parseDateArray"), uu = a(function(r) {
    if (!r)
      return null;
    var e = ze.create(r, function(t) {
      return t !== null && (t = ji(t)), t;
    });
    return e.parse();
  }, "parseIntervalArray"), cu = a(function(r) {
    return r ? Ve.parse(r, At(Hi)) : null;
  }, "parseByteAArray"), ur = a(function(r) {
    return parseInt(r, 10);
  }, "parseInteger"), Gi = a(function(r) {
    var e = String(r);
    return /^\d+$/.test(e) ? e : r;
  }, "parseBigInteger"), Wi = a(function(r) {
    return r ? Ve.parse(r, At(JSON.parse)) : null;
  }, "parseJsonArray"), cr = a(
    function(r) {
      return r[0] !== "(" ? null : (r = r.substring(1, r.length - 1).split(","), { x: parseFloat(r[0]), y: parseFloat(
        r[1]
      ) });
    },
    "parsePoint"
  ), lu = a(function(r) {
    if (r[0] !== "<" && r[1] !== "(") return null;
    for (var e = "(", t = "", n = false, i = 2; i < r.length - 1; i++) {
      if (n || (e += r[i]), r[i] === ")") {
        n = true;
        continue;
      } else if (!n) continue;
      r[i] !== "," && (t += r[i]);
    }
    var s = cr(e);
    return s.radius = parseFloat(t), s;
  }, "parseCircle"), fu = a(function(r) {
    r(20, Gi), r(21, ur), r(23, ur), r(26, ur), r(700, parseFloat), r(701, parseFloat), r(16, $i), r(1082, Et), r(1114, Et), r(1184, Et), r(
      600,
      cr
    ), r(651, ee), r(718, lu), r(1e3, iu), r(1001, cu), r(1005, sr), r(1007, sr), r(1028, sr), r(1016, ou), r(1017, au), r(1021, or), r(1022, or), r(1231, or), r(1014, ee), r(1015, ee), r(1008, ee), r(1009, ee), r(1040, ee), r(1041, ee), r(
      1115,
      ar
    ), r(1182, ar), r(1185, ar), r(1186, ji), r(1187, uu), r(17, Hi), r(114, JSON.parse.bind(JSON)), r(3802, JSON.parse.bind(JSON)), r(199, Wi), r(3807, Wi), r(3907, ee), r(2951, ee), r(791, ee), r(1183, ee), r(1270, ee);
  }, "init");
  Vi.exports = { init: fu };
});
var Yi = T((Zf, Ki) => {
  "use strict";
  h();
  var K = 1e6;
  function hu(r) {
    var e = r.readInt32BE(0), t = r.readUInt32BE(
      4
    ), n = "";
    e < 0 && (e = ~e + (t === 0), t = ~t + 1 >>> 0, n = "-");
    var i = "", s, o, u, c, l, f;
    {
      if (s = e % K, e = e / K >>> 0, o = 4294967296 * s + t, t = o / K >>> 0, u = "" + (o - K * t), t === 0 && e === 0) return n + u + i;
      for (c = "", l = 6 - u.length, f = 0; f < l; f++) c += "0";
      i = c + u + i;
    }
    {
      if (s = e % K, e = e / K >>> 0, o = 4294967296 * s + t, t = o / K >>> 0, u = "" + (o - K * t), t === 0 && e === 0) return n + u + i;
      for (c = "", l = 6 - u.length, f = 0; f < l; f++) c += "0";
      i = c + u + i;
    }
    {
      if (s = e % K, e = e / K >>> 0, o = 4294967296 * s + t, t = o / K >>> 0, u = "" + (o - K * t), t === 0 && e === 0) return n + u + i;
      for (c = "", l = 6 - u.length, f = 0; f < l; f++) c += "0";
      i = c + u + i;
    }
    return s = e % K, o = 4294967296 * s + t, u = "" + o % K, n + u + i;
  }
  __name(hu, "hu");
  a(hu, "readInt8");
  Ki.exports = hu;
});
var ts = T((eh, es) => {
  h();
  var du = Yi(), B = a(function(r, e, t, n, i) {
    t = t || 0, n = n || false, i = i || function(w, S, k) {
      return w * Math.pow(2, k) + S;
    };
    var s = t >> 3, o = a(function(w) {
      return n ? ~w & 255 : w;
    }, "inv"), u = 255, c = 8 - t % 8;
    e < c && (u = 255 << 8 - e & 255, c = e), t && (u = u >> t % 8);
    var l = 0;
    t % 8 + e >= 8 && (l = i(0, o(r[s]) & u, c));
    for (var f = e + t >> 3, m = s + 1; m < f; m++) l = i(l, o(
      r[m]
    ), 8);
    var g = (e + t) % 8;
    return g > 0 && (l = i(l, o(r[f]) >> 8 - g, g)), l;
  }, "parseBits"), Xi = a(function(r, e, t) {
    var n = Math.pow(2, t - 1) - 1, i = B(r, 1), s = B(r, t, 1);
    if (s === 0) return 0;
    var o = 1, u = a(function(l, f, m) {
      l === 0 && (l = 1);
      for (var g = 1; g <= m; g++) o /= 2, (f & 1 << m - g) > 0 && (l += o);
      return l;
    }, "parsePrecisionBits"), c = B(r, e, t + 1, false, u);
    return s == Math.pow(
      2,
      t + 1
    ) - 1 ? c === 0 ? i === 0 ? 1 / 0 : -1 / 0 : NaN : (i === 0 ? 1 : -1) * Math.pow(2, s - n) * c;
  }, "parseFloatFromBits"), pu = a(function(r) {
    return B(r, 1) == 1 ? -1 * (B(r, 15, 1, true) + 1) : B(r, 15, 1);
  }, "parseInt16"), Zi = a(function(r) {
    return B(r, 1) == 1 ? -1 * (B(
      r,
      31,
      1,
      true
    ) + 1) : B(r, 31, 1);
  }, "parseInt32"), yu = a(function(r) {
    return Xi(r, 23, 8);
  }, "parseFloat32"), mu = a(function(r) {
    return Xi(r, 52, 11);
  }, "parseFloat64"), gu = a(function(r) {
    var e = B(r, 16, 32);
    if (e == 49152) return NaN;
    for (var t = Math.pow(1e4, B(r, 16, 16)), n = 0, i = [], s = B(r, 16), o = 0; o < s; o++) n += B(r, 16, 64 + 16 * o) * t, t /= 1e4;
    var u = Math.pow(10, B(
      r,
      16,
      48
    ));
    return (e === 0 ? 1 : -1) * Math.round(n * u) / u;
  }, "parseNumeric"), Ji = a(function(r, e) {
    var t = B(e, 1), n = B(
      e,
      63,
      1
    ), i = new Date((t === 0 ? 1 : -1) * n / 1e3 + 9466848e5);
    return r || i.setTime(i.getTime() + i.getTimezoneOffset() * 6e4), i.usec = n % 1e3, i.getMicroSeconds = function() {
      return this.usec;
    }, i.setMicroSeconds = function(s) {
      this.usec = s;
    }, i.getUTCMicroSeconds = function() {
      return this.usec;
    }, i;
  }, "parseDate"), Ke = a(
    function(r) {
      for (var e = B(
        r,
        32
      ), t = B(r, 32, 32), n = B(r, 32, 64), i = 96, s = [], o = 0; o < e; o++) s[o] = B(r, 32, i), i += 32, i += 32;
      var u = a(function(l) {
        var f = B(r, 32, i);
        if (i += 32, f == 4294967295) return null;
        var m;
        if (l == 23 || l == 20) return m = B(r, f * 8, i), i += f * 8, m;
        if (l == 25) return m = r.toString(this.encoding, i >> 3, (i += f << 3) >> 3), m;
        console.log("ERROR: ElementType not implemented: " + l);
      }, "parseElement"), c = a(function(l, f) {
        var m = [], g;
        if (l.length > 1) {
          var w = l.shift();
          for (g = 0; g < w; g++) m[g] = c(l, f);
          l.unshift(w);
        } else for (g = 0; g < l[0]; g++) m[g] = u(f);
        return m;
      }, "parse");
      return c(s, n);
    },
    "parseArray"
  ), wu = a(function(r) {
    return r.toString("utf8");
  }, "parseText"), bu = a(function(r) {
    return r === null ? null : B(r, 8) > 0;
  }, "parseBool"), xu = a(function(r) {
    r(20, du), r(21, pu), r(23, Zi), r(26, Zi), r(1700, gu), r(700, yu), r(701, mu), r(16, bu), r(1114, Ji.bind(null, false)), r(1184, Ji.bind(null, true)), r(1e3, Ke), r(1007, Ke), r(1016, Ke), r(1008, Ke), r(1009, Ke), r(25, wu);
  }, "init");
  es.exports = { init: xu };
});
var ns = T((nh, rs) => {
  h();
  rs.exports = {
    BOOL: 16,
    BYTEA: 17,
    CHAR: 18,
    INT8: 20,
    INT2: 21,
    INT4: 23,
    REGPROC: 24,
    TEXT: 25,
    OID: 26,
    TID: 27,
    XID: 28,
    CID: 29,
    JSON: 114,
    XML: 142,
    PG_NODE_TREE: 194,
    SMGR: 210,
    PATH: 602,
    POLYGON: 604,
    CIDR: 650,
    FLOAT4: 700,
    FLOAT8: 701,
    ABSTIME: 702,
    RELTIME: 703,
    TINTERVAL: 704,
    CIRCLE: 718,
    MACADDR8: 774,
    MONEY: 790,
    MACADDR: 829,
    INET: 869,
    ACLITEM: 1033,
    BPCHAR: 1042,
    VARCHAR: 1043,
    DATE: 1082,
    TIME: 1083,
    TIMESTAMP: 1114,
    TIMESTAMPTZ: 1184,
    INTERVAL: 1186,
    TIMETZ: 1266,
    BIT: 1560,
    VARBIT: 1562,
    NUMERIC: 1700,
    REFCURSOR: 1790,
    REGPROCEDURE: 2202,
    REGOPER: 2203,
    REGOPERATOR: 2204,
    REGCLASS: 2205,
    REGTYPE: 2206,
    UUID: 2950,
    TXID_SNAPSHOT: 2970,
    PG_LSN: 3220,
    PG_NDISTINCT: 3361,
    PG_DEPENDENCIES: 3402,
    TSVECTOR: 3614,
    TSQUERY: 3615,
    GTSVECTOR: 3642,
    REGCONFIG: 3734,
    REGDICTIONARY: 3769,
    JSONB: 3802,
    REGNAMESPACE: 4089,
    REGROLE: 4096
  };
});
var Je = T((Ze) => {
  h();
  var vu = zi(), Su = ts(), Eu = rr(), Au = ns();
  Ze.getTypeParser = Cu;
  Ze.setTypeParser = _u;
  Ze.arrayParser = Eu;
  Ze.builtins = Au;
  var Ye = { text: {}, binary: {} };
  function is(r) {
    return String(r);
  }
  __name(is, "is");
  a(is, "noParse");
  function Cu(r, e) {
    return e = e || "text", Ye[e] && Ye[e][r] || is;
  }
  __name(Cu, "Cu");
  a(Cu, "getTypeParser");
  function _u(r, e, t) {
    typeof e == "function" && (t = e, e = "text"), Ye[e][r] = t;
  }
  __name(_u, "_u");
  a(_u, "setTypeParser");
  vu.init(function(r, e) {
    Ye.text[r] = e;
  });
  Su.init(function(r, e) {
    Ye.binary[r] = e;
  });
});
var _t = T((uh, ss) => {
  "use strict";
  h();
  var Tu = Je();
  function Ct(r) {
    this._types = r || Tu, this.text = {}, this.binary = {};
  }
  __name(Ct, "Ct");
  a(Ct, "TypeOverrides");
  Ct.prototype.getOverrides = function(r) {
    switch (r) {
      case "text":
        return this.text;
      case "binary":
        return this.binary;
      default:
        return {};
    }
  };
  Ct.prototype.setTypeParser = function(r, e, t) {
    typeof e == "function" && (t = e, e = "text"), this.getOverrides(e)[r] = t;
  };
  Ct.prototype.getTypeParser = function(r, e) {
    return e = e || "text", this.getOverrides(e)[r] || this._types.getTypeParser(r, e);
  };
  ss.exports = Ct;
});
function Xe(r) {
  let e = 1779033703, t = 3144134277, n = 1013904242, i = 2773480762, s = 1359893119, o = 2600822924, u = 528734635, c = 1541459225, l = 0, f = 0, m = [
    1116352408,
    1899447441,
    3049323471,
    3921009573,
    961987163,
    1508970993,
    2453635748,
    2870763221,
    3624381080,
    310598401,
    607225278,
    1426881987,
    1925078388,
    2162078206,
    2614888103,
    3248222580,
    3835390401,
    4022224774,
    264347078,
    604807628,
    770255983,
    1249150122,
    1555081692,
    1996064986,
    2554220882,
    2821834349,
    2952996808,
    3210313671,
    3336571891,
    3584528711,
    113926993,
    338241895,
    666307205,
    773529912,
    1294757372,
    1396182291,
    1695183700,
    1986661051,
    2177026350,
    2456956037,
    2730485921,
    2820302411,
    3259730800,
    3345764771,
    3516065817,
    3600352804,
    4094571909,
    275423344,
    430227734,
    506948616,
    659060556,
    883997877,
    958139571,
    1322822218,
    1537002063,
    1747873779,
    1955562222,
    2024104815,
    2227730452,
    2361852424,
    2428436474,
    2756734187,
    3204031479,
    3329325298
  ], g = a((I, C) => I >>> C | I << 32 - C, "rrot"), w = new Uint32Array(64), S = new Uint8Array(64), k = a(() => {
    for (let R = 0, $ = 0; R < 16; R++, $ += 4) w[R] = S[$] << 24 | S[$ + 1] << 16 | S[$ + 2] << 8 | S[$ + 3];
    for (let R = 16; R < 64; R++) {
      let $ = g(w[R - 15], 7) ^ g(w[R - 15], 18) ^ w[R - 15] >>> 3, Ee = g(
        w[R - 2],
        17
      ) ^ g(w[R - 2], 19) ^ w[R - 2] >>> 10;
      w[R] = w[R - 16] + $ + w[R - 7] + Ee | 0;
    }
    let I = e, C = t, re = n, ne = i, H = s, oe = o, ae = u, me = c;
    for (let R = 0; R < 64; R++) {
      let $ = g(H, 6) ^ g(H, 11) ^ g(H, 25), Ee = H & oe ^ ~H & ae, ue = me + $ + Ee + m[R] + w[R] | 0, Te = g(I, 2) ^ g(
        I,
        13
      ) ^ g(I, 22), ce = I & C ^ I & re ^ C & re, G = Te + ce | 0;
      me = ae, ae = oe, oe = H, H = ne + ue | 0, ne = re, re = C, C = I, I = ue + G | 0;
    }
    e = e + I | 0, t = t + C | 0, n = n + re | 0, i = i + ne | 0, s = s + H | 0, o = o + oe | 0, u = u + ae | 0, c = c + me | 0, f = 0;
  }, "process"), D = a(
    (I) => {
      typeof I == "string" && (I = new TextEncoder().encode(I));
      for (let C = 0; C < I.length; C++) S[f++] = I[C], f === 64 && k();
      l += I.length;
    },
    "add"
  ), he = a(() => {
    if (S[f++] = 128, f == 64 && k(), f + 8 > 64) {
      for (; f < 64; ) S[f++] = 0;
      k();
    }
    for (; f < 58; ) S[f++] = 0;
    let I = l * 8;
    S[f++] = I / 1099511627776 & 255, S[f++] = I / 4294967296 & 255, S[f++] = I >>> 24, S[f++] = I >>> 16 & 255, S[f++] = I >>> 8 & 255, S[f++] = I & 255, k();
    let C = new Uint8Array(32);
    return C[0] = e >>> 24, C[1] = e >>> 16 & 255, C[2] = e >>> 8 & 255, C[3] = e & 255, C[4] = t >>> 24, C[5] = t >>> 16 & 255, C[6] = t >>> 8 & 255, C[7] = t & 255, C[8] = n >>> 24, C[9] = n >>> 16 & 255, C[10] = n >>> 8 & 255, C[11] = n & 255, C[12] = i >>> 24, C[13] = i >>> 16 & 255, C[14] = i >>> 8 & 255, C[15] = i & 255, C[16] = s >>> 24, C[17] = s >>> 16 & 255, C[18] = s >>> 8 & 255, C[19] = s & 255, C[20] = o >>> 24, C[21] = o >>> 16 & 255, C[22] = o >>> 8 & 255, C[23] = o & 255, C[24] = u >>> 24, C[25] = u >>> 16 & 255, C[26] = u >>> 8 & 255, C[27] = u & 255, C[28] = c >>> 24, C[29] = c >>> 16 & 255, C[30] = c >>> 8 & 255, C[31] = c & 255, C;
  }, "digest");
  return r === void 0 ? { add: D, digest: he } : (D(r), he());
}
__name(Xe, "Xe");
var os = V(() => {
  "use strict";
  h();
  a(Xe, "sha256");
});
var M;
var et;
var as = V(() => {
  "use strict";
  h();
  M = class M2 {
    static {
      __name(this, "M");
    }
    constructor() {
      E(this, "_dataLength", 0);
      E(this, "_bufferLength", 0);
      E(this, "_state", new Int32Array(4));
      E(this, "_buffer", new ArrayBuffer(68));
      E(this, "_buffer8");
      E(this, "_buffer32");
      this._buffer8 = new Uint8Array(this._buffer, 0, 68), this._buffer32 = new Uint32Array(this._buffer, 0, 17), this.start();
    }
    static hashByteArray(e, t = false) {
      return this.onePassHasher.start().appendByteArray(
        e
      ).end(t);
    }
    static hashStr(e, t = false) {
      return this.onePassHasher.start().appendStr(e).end(t);
    }
    static hashAsciiStr(e, t = false) {
      return this.onePassHasher.start().appendAsciiStr(e).end(t);
    }
    static _hex(e) {
      let t = M2.hexChars, n = M2.hexOut, i, s, o, u;
      for (u = 0; u < 4; u += 1) for (s = u * 8, i = e[u], o = 0; o < 8; o += 2) n[s + 1 + o] = t.charAt(i & 15), i >>>= 4, n[s + 0 + o] = t.charAt(
        i & 15
      ), i >>>= 4;
      return n.join("");
    }
    static _md5cycle(e, t) {
      let n = e[0], i = e[1], s = e[2], o = e[3];
      n += (i & s | ~i & o) + t[0] - 680876936 | 0, n = (n << 7 | n >>> 25) + i | 0, o += (n & i | ~n & s) + t[1] - 389564586 | 0, o = (o << 12 | o >>> 20) + n | 0, s += (o & n | ~o & i) + t[2] + 606105819 | 0, s = (s << 17 | s >>> 15) + o | 0, i += (s & o | ~s & n) + t[3] - 1044525330 | 0, i = (i << 22 | i >>> 10) + s | 0, n += (i & s | ~i & o) + t[4] - 176418897 | 0, n = (n << 7 | n >>> 25) + i | 0, o += (n & i | ~n & s) + t[5] + 1200080426 | 0, o = (o << 12 | o >>> 20) + n | 0, s += (o & n | ~o & i) + t[6] - 1473231341 | 0, s = (s << 17 | s >>> 15) + o | 0, i += (s & o | ~s & n) + t[7] - 45705983 | 0, i = (i << 22 | i >>> 10) + s | 0, n += (i & s | ~i & o) + t[8] + 1770035416 | 0, n = (n << 7 | n >>> 25) + i | 0, o += (n & i | ~n & s) + t[9] - 1958414417 | 0, o = (o << 12 | o >>> 20) + n | 0, s += (o & n | ~o & i) + t[10] - 42063 | 0, s = (s << 17 | s >>> 15) + o | 0, i += (s & o | ~s & n) + t[11] - 1990404162 | 0, i = (i << 22 | i >>> 10) + s | 0, n += (i & s | ~i & o) + t[12] + 1804603682 | 0, n = (n << 7 | n >>> 25) + i | 0, o += (n & i | ~n & s) + t[13] - 40341101 | 0, o = (o << 12 | o >>> 20) + n | 0, s += (o & n | ~o & i) + t[14] - 1502002290 | 0, s = (s << 17 | s >>> 15) + o | 0, i += (s & o | ~s & n) + t[15] + 1236535329 | 0, i = (i << 22 | i >>> 10) + s | 0, n += (i & o | s & ~o) + t[1] - 165796510 | 0, n = (n << 5 | n >>> 27) + i | 0, o += (n & s | i & ~s) + t[6] - 1069501632 | 0, o = (o << 9 | o >>> 23) + n | 0, s += (o & i | n & ~i) + t[11] + 643717713 | 0, s = (s << 14 | s >>> 18) + o | 0, i += (s & n | o & ~n) + t[0] - 373897302 | 0, i = (i << 20 | i >>> 12) + s | 0, n += (i & o | s & ~o) + t[5] - 701558691 | 0, n = (n << 5 | n >>> 27) + i | 0, o += (n & s | i & ~s) + t[10] + 38016083 | 0, o = (o << 9 | o >>> 23) + n | 0, s += (o & i | n & ~i) + t[15] - 660478335 | 0, s = (s << 14 | s >>> 18) + o | 0, i += (s & n | o & ~n) + t[4] - 405537848 | 0, i = (i << 20 | i >>> 12) + s | 0, n += (i & o | s & ~o) + t[9] + 568446438 | 0, n = (n << 5 | n >>> 27) + i | 0, o += (n & s | i & ~s) + t[14] - 1019803690 | 0, o = (o << 9 | o >>> 23) + n | 0, s += (o & i | n & ~i) + t[3] - 187363961 | 0, s = (s << 14 | s >>> 18) + o | 0, i += (s & n | o & ~n) + t[8] + 1163531501 | 0, i = (i << 20 | i >>> 12) + s | 0, n += (i & o | s & ~o) + t[13] - 1444681467 | 0, n = (n << 5 | n >>> 27) + i | 0, o += (n & s | i & ~s) + t[2] - 51403784 | 0, o = (o << 9 | o >>> 23) + n | 0, s += (o & i | n & ~i) + t[7] + 1735328473 | 0, s = (s << 14 | s >>> 18) + o | 0, i += (s & n | o & ~n) + t[12] - 1926607734 | 0, i = (i << 20 | i >>> 12) + s | 0, n += (i ^ s ^ o) + t[5] - 378558 | 0, n = (n << 4 | n >>> 28) + i | 0, o += (n ^ i ^ s) + t[8] - 2022574463 | 0, o = (o << 11 | o >>> 21) + n | 0, s += (o ^ n ^ i) + t[11] + 1839030562 | 0, s = (s << 16 | s >>> 16) + o | 0, i += (s ^ o ^ n) + t[14] - 35309556 | 0, i = (i << 23 | i >>> 9) + s | 0, n += (i ^ s ^ o) + t[1] - 1530992060 | 0, n = (n << 4 | n >>> 28) + i | 0, o += (n ^ i ^ s) + t[4] + 1272893353 | 0, o = (o << 11 | o >>> 21) + n | 0, s += (o ^ n ^ i) + t[7] - 155497632 | 0, s = (s << 16 | s >>> 16) + o | 0, i += (s ^ o ^ n) + t[10] - 1094730640 | 0, i = (i << 23 | i >>> 9) + s | 0, n += (i ^ s ^ o) + t[13] + 681279174 | 0, n = (n << 4 | n >>> 28) + i | 0, o += (n ^ i ^ s) + t[0] - 358537222 | 0, o = (o << 11 | o >>> 21) + n | 0, s += (o ^ n ^ i) + t[3] - 722521979 | 0, s = (s << 16 | s >>> 16) + o | 0, i += (s ^ o ^ n) + t[6] + 76029189 | 0, i = (i << 23 | i >>> 9) + s | 0, n += (i ^ s ^ o) + t[9] - 640364487 | 0, n = (n << 4 | n >>> 28) + i | 0, o += (n ^ i ^ s) + t[12] - 421815835 | 0, o = (o << 11 | o >>> 21) + n | 0, s += (o ^ n ^ i) + t[15] + 530742520 | 0, s = (s << 16 | s >>> 16) + o | 0, i += (s ^ o ^ n) + t[2] - 995338651 | 0, i = (i << 23 | i >>> 9) + s | 0, n += (s ^ (i | ~o)) + t[0] - 198630844 | 0, n = (n << 6 | n >>> 26) + i | 0, o += (i ^ (n | ~s)) + t[7] + 1126891415 | 0, o = (o << 10 | o >>> 22) + n | 0, s += (n ^ (o | ~i)) + t[14] - 1416354905 | 0, s = (s << 15 | s >>> 17) + o | 0, i += (o ^ (s | ~n)) + t[5] - 57434055 | 0, i = (i << 21 | i >>> 11) + s | 0, n += (s ^ (i | ~o)) + t[12] + 1700485571 | 0, n = (n << 6 | n >>> 26) + i | 0, o += (i ^ (n | ~s)) + t[3] - 1894986606 | 0, o = (o << 10 | o >>> 22) + n | 0, s += (n ^ (o | ~i)) + t[10] - 1051523 | 0, s = (s << 15 | s >>> 17) + o | 0, i += (o ^ (s | ~n)) + t[1] - 2054922799 | 0, i = (i << 21 | i >>> 11) + s | 0, n += (s ^ (i | ~o)) + t[8] + 1873313359 | 0, n = (n << 6 | n >>> 26) + i | 0, o += (i ^ (n | ~s)) + t[15] - 30611744 | 0, o = (o << 10 | o >>> 22) + n | 0, s += (n ^ (o | ~i)) + t[6] - 1560198380 | 0, s = (s << 15 | s >>> 17) + o | 0, i += (o ^ (s | ~n)) + t[13] + 1309151649 | 0, i = (i << 21 | i >>> 11) + s | 0, n += (s ^ (i | ~o)) + t[4] - 145523070 | 0, n = (n << 6 | n >>> 26) + i | 0, o += (i ^ (n | ~s)) + t[11] - 1120210379 | 0, o = (o << 10 | o >>> 22) + n | 0, s += (n ^ (o | ~i)) + t[2] + 718787259 | 0, s = (s << 15 | s >>> 17) + o | 0, i += (o ^ (s | ~n)) + t[9] - 343485551 | 0, i = (i << 21 | i >>> 11) + s | 0, e[0] = n + e[0] | 0, e[1] = i + e[1] | 0, e[2] = s + e[2] | 0, e[3] = o + e[3] | 0;
    }
    start() {
      return this._dataLength = 0, this._bufferLength = 0, this._state.set(M2.stateIdentity), this;
    }
    appendStr(e) {
      let t = this._buffer8, n = this._buffer32, i = this._bufferLength, s, o;
      for (o = 0; o < e.length; o += 1) {
        if (s = e.charCodeAt(o), s < 128) t[i++] = s;
        else if (s < 2048) t[i++] = (s >>> 6) + 192, t[i++] = s & 63 | 128;
        else if (s < 55296 || s > 56319) t[i++] = (s >>> 12) + 224, t[i++] = s >>> 6 & 63 | 128, t[i++] = s & 63 | 128;
        else {
          if (s = (s - 55296) * 1024 + (e.charCodeAt(++o) - 56320) + 65536, s > 1114111) throw new Error(
            "Unicode standard supports code points up to U+10FFFF"
          );
          t[i++] = (s >>> 18) + 240, t[i++] = s >>> 12 & 63 | 128, t[i++] = s >>> 6 & 63 | 128, t[i++] = s & 63 | 128;
        }
        i >= 64 && (this._dataLength += 64, M2._md5cycle(this._state, n), i -= 64, n[0] = n[16]);
      }
      return this._bufferLength = i, this;
    }
    appendAsciiStr(e) {
      let t = this._buffer8, n = this._buffer32, i = this._bufferLength, s, o = 0;
      for (; ; ) {
        for (s = Math.min(e.length - o, 64 - i); s--; ) t[i++] = e.charCodeAt(o++);
        if (i < 64) break;
        this._dataLength += 64, M2._md5cycle(this._state, n), i = 0;
      }
      return this._bufferLength = i, this;
    }
    appendByteArray(e) {
      let t = this._buffer8, n = this._buffer32, i = this._bufferLength, s, o = 0;
      for (; ; ) {
        for (s = Math.min(e.length - o, 64 - i); s--; ) t[i++] = e[o++];
        if (i < 64) break;
        this._dataLength += 64, M2._md5cycle(this._state, n), i = 0;
      }
      return this._bufferLength = i, this;
    }
    getState() {
      let e = this._state;
      return { buffer: String.fromCharCode.apply(null, Array.from(this._buffer8)), buflen: this._bufferLength, length: this._dataLength, state: [e[0], e[1], e[2], e[3]] };
    }
    setState(e) {
      let t = e.buffer, n = e.state, i = this._state, s;
      for (this._dataLength = e.length, this._bufferLength = e.buflen, i[0] = n[0], i[1] = n[1], i[2] = n[2], i[3] = n[3], s = 0; s < t.length; s += 1) this._buffer8[s] = t.charCodeAt(s);
    }
    end(e = false) {
      let t = this._bufferLength, n = this._buffer8, i = this._buffer32, s = (t >> 2) + 1;
      this._dataLength += t;
      let o = this._dataLength * 8;
      if (n[t] = 128, n[t + 1] = n[t + 2] = n[t + 3] = 0, i.set(M2.buffer32Identity.subarray(s), s), t > 55 && (M2._md5cycle(this._state, i), i.set(M2.buffer32Identity)), o <= 4294967295) i[14] = o;
      else {
        let u = o.toString(16).match(/(.*?)(.{0,8})$/);
        if (u === null) return;
        let c = parseInt(
          u[2],
          16
        ), l = parseInt(u[1], 16) || 0;
        i[14] = c, i[15] = l;
      }
      return M2._md5cycle(this._state, i), e ? this._state : M2._hex(
        this._state
      );
    }
  };
  a(M, "Md5"), E(M, "stateIdentity", new Int32Array([1732584193, -271733879, -1732584194, 271733878])), E(M, "buffer32Identity", new Int32Array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])), E(M, "hexChars", "0123456789abcdef"), E(M, "hexOut", []), E(M, "onePassHasher", new M());
  et = M;
});
var lr = {};
se(lr, { createHash: /* @__PURE__ */ __name(() => Pu, "createHash"), createHmac: /* @__PURE__ */ __name(() => Ru, "createHmac"), randomBytes: /* @__PURE__ */ __name(() => Iu, "randomBytes") });
function Iu(r) {
  return crypto.getRandomValues(p.alloc(r));
}
__name(Iu, "Iu");
function Pu(r) {
  if (r === "sha256") return { update: a(function(e) {
    return { digest: a(
      function() {
        return p.from(Xe(e));
      },
      "digest"
    ) };
  }, "update") };
  if (r === "md5") return { update: a(function(e) {
    return {
      digest: a(function() {
        return typeof e == "string" ? et.hashStr(e) : et.hashByteArray(e);
      }, "digest")
    };
  }, "update") };
  throw new Error(`Hash type '${r}' not supported`);
}
__name(Pu, "Pu");
function Ru(r, e) {
  if (r !== "sha256") throw new Error(`Only sha256 is supported (requested: '${r}')`);
  return { update: a(function(t) {
    return { digest: a(
      function() {
        typeof e == "string" && (e = new TextEncoder().encode(e)), typeof t == "string" && (t = new TextEncoder().encode(
          t
        ));
        let n = e.length;
        if (n > 64) e = Xe(e);
        else if (n < 64) {
          let c = new Uint8Array(64);
          c.set(e), e = c;
        }
        let i = new Uint8Array(
          64
        ), s = new Uint8Array(64);
        for (let c = 0; c < 64; c++) i[c] = 54 ^ e[c], s[c] = 92 ^ e[c];
        let o = new Uint8Array(t.length + 64);
        o.set(i, 0), o.set(t, 64);
        let u = new Uint8Array(96);
        return u.set(s, 0), u.set(Xe(o), 64), p.from(Xe(u));
      },
      "digest"
    ) };
  }, "update") };
}
__name(Ru, "Ru");
var fr = V(() => {
  "use strict";
  h();
  os();
  as();
  a(Iu, "randomBytes");
  a(Pu, "createHash");
  a(Ru, "createHmac");
});
var tt = T((vh, hr) => {
  "use strict";
  h();
  hr.exports = {
    host: "localhost",
    user: y.platform === "win32" ? y.env.USERNAME : y.env.USER,
    database: void 0,
    password: null,
    connectionString: void 0,
    port: 5432,
    rows: 0,
    binary: false,
    max: 10,
    idleTimeoutMillis: 3e4,
    client_encoding: "",
    ssl: false,
    application_name: void 0,
    fallback_application_name: void 0,
    options: void 0,
    parseInputDatesAsUTC: false,
    statement_timeout: false,
    lock_timeout: false,
    idle_in_transaction_session_timeout: false,
    query_timeout: false,
    connect_timeout: 0,
    keepalives: 1,
    keepalives_idle: 0
  };
  var ke = Je(), Lu = ke.getTypeParser(20, "text"), Bu = ke.getTypeParser(
    1016,
    "text"
  );
  hr.exports.__defineSetter__("parseInt8", function(r) {
    ke.setTypeParser(20, "text", r ? ke.getTypeParser(
      23,
      "text"
    ) : Lu), ke.setTypeParser(1016, "text", r ? ke.getTypeParser(1007, "text") : Bu);
  });
});
var rt = T((Eh, cs) => {
  "use strict";
  h();
  var Fu = (fr(), O(lr)), Mu = tt();
  function ku(r) {
    var e = r.replace(
      /\\/g,
      "\\\\"
    ).replace(/"/g, '\\"');
    return '"' + e + '"';
  }
  __name(ku, "ku");
  a(ku, "escapeElement");
  function us(r) {
    for (var e = "{", t = 0; t < r.length; t++) t > 0 && (e = e + ","), r[t] === null || typeof r[t] > "u" ? e = e + "NULL" : Array.isArray(r[t]) ? e = e + us(r[t]) : r[t] instanceof p ? e += "\\\\x" + r[t].toString("hex") : e += ku(Tt(r[t]));
    return e = e + "}", e;
  }
  __name(us, "us");
  a(us, "arrayString");
  var Tt = a(function(r, e) {
    if (r == null) return null;
    if (r instanceof p) return r;
    if (ArrayBuffer.isView(r)) {
      var t = p.from(r.buffer, r.byteOffset, r.byteLength);
      return t.length === r.byteLength ? t : t.slice(r.byteOffset, r.byteOffset + r.byteLength);
    }
    return r instanceof Date ? Mu.parseInputDatesAsUTC ? Qu(r) : Uu(r) : Array.isArray(r) ? us(r) : typeof r == "object" ? Ou(r, e) : r.toString();
  }, "prepareValue");
  function Ou(r, e) {
    if (r && typeof r.toPostgres == "function") {
      if (e = e || [], e.indexOf(r) !== -1) throw new Error('circular reference detected while preparing "' + r + '" for query');
      return e.push(r), Tt(r.toPostgres(Tt), e);
    }
    return JSON.stringify(r);
  }
  __name(Ou, "Ou");
  a(Ou, "prepareObject");
  function W(r, e) {
    for (r = "" + r; r.length < e; ) r = "0" + r;
    return r;
  }
  __name(W, "W");
  a(W, "pad");
  function Uu(r) {
    var e = -r.getTimezoneOffset(), t = r.getFullYear(), n = t < 1;
    n && (t = Math.abs(t) + 1);
    var i = W(t, 4) + "-" + W(r.getMonth() + 1, 2) + "-" + W(r.getDate(), 2) + "T" + W(
      r.getHours(),
      2
    ) + ":" + W(r.getMinutes(), 2) + ":" + W(r.getSeconds(), 2) + "." + W(r.getMilliseconds(), 3);
    return e < 0 ? (i += "-", e *= -1) : i += "+", i += W(Math.floor(e / 60), 2) + ":" + W(e % 60, 2), n && (i += " BC"), i;
  }
  __name(Uu, "Uu");
  a(Uu, "dateToString");
  function Qu(r) {
    var e = r.getUTCFullYear(), t = e < 1;
    t && (e = Math.abs(e) + 1);
    var n = W(e, 4) + "-" + W(r.getUTCMonth() + 1, 2) + "-" + W(r.getUTCDate(), 2) + "T" + W(r.getUTCHours(), 2) + ":" + W(r.getUTCMinutes(), 2) + ":" + W(r.getUTCSeconds(), 2) + "." + W(
      r.getUTCMilliseconds(),
      3
    );
    return n += "+00:00", t && (n += " BC"), n;
  }
  __name(Qu, "Qu");
  a(Qu, "dateToStringUTC");
  function Du(r, e, t) {
    return r = typeof r == "string" ? { text: r } : r, e && (typeof e == "function" ? r.callback = e : r.values = e), t && (r.callback = t), r;
  }
  __name(Du, "Du");
  a(Du, "normalizeQueryConfig");
  var dr = a(function(r) {
    return Fu.createHash("md5").update(r, "utf-8").digest("hex");
  }, "md5"), qu = a(
    function(r, e, t) {
      var n = dr(e + r), i = dr(p.concat([p.from(n), t]));
      return "md5" + i;
    },
    "postgresMd5PasswordHash"
  );
  cs.exports = {
    prepareValue: a(function(e) {
      return Tt(e);
    }, "prepareValueWrapper"),
    normalizeQueryConfig: Du,
    postgresMd5PasswordHash: qu,
    md5: dr
  };
});
var nt = {};
se(nt, { default: /* @__PURE__ */ __name(() => ju, "default") });
var ju;
var it = V(() => {
  "use strict";
  h();
  ju = {};
});
var xs = T((Dh, bs) => {
  "use strict";
  h();
  var pr = (fr(), O(lr));
  function Hu(r) {
    if (r.indexOf("SCRAM-SHA-256") === -1) throw new Error("SASL: Only mechanism SCRAM-SHA-256 is currently supported");
    let e = pr.randomBytes(
      18
    ).toString("base64");
    return { mechanism: "SCRAM-SHA-256", clientNonce: e, response: "n,,n=*,r=" + e, message: "SASLInitialResponse" };
  }
  __name(Hu, "Hu");
  a(Hu, "startSession");
  function $u(r, e, t) {
    if (r.message !== "SASLInitialResponse") throw new Error(
      "SASL: Last message was not SASLInitialResponse"
    );
    if (typeof e != "string") throw new Error("SASL: SCRAM-SERVER-FIRST-MESSAGE: client password must be a string");
    if (typeof t != "string") throw new Error("SASL: SCRAM-SERVER-FIRST-MESSAGE: serverData must be a string");
    let n = zu(t);
    if (n.nonce.startsWith(r.clientNonce)) {
      if (n.nonce.length === r.clientNonce.length) throw new Error("SASL: SCRAM-SERVER-FIRST-MESSAGE: server nonce is too short");
    } else throw new Error("SASL: SCRAM-SERVER-FIRST-MESSAGE: server nonce does not start with client nonce");
    var i = p.from(n.salt, "base64"), s = Zu(e, i, n.iteration), o = Oe(s, "Client Key"), u = Yu(
      o
    ), c = "n=*,r=" + r.clientNonce, l = "r=" + n.nonce + ",s=" + n.salt + ",i=" + n.iteration, f = "c=biws,r=" + n.nonce, m = c + "," + l + "," + f, g = Oe(u, m), w = ws(o, g), S = w.toString("base64"), k = Oe(s, "Server Key"), D = Oe(k, m);
    r.message = "SASLResponse", r.serverSignature = D.toString("base64"), r.response = f + ",p=" + S;
  }
  __name($u, "$u");
  a($u, "continueSession");
  function Gu(r, e) {
    if (r.message !== "SASLResponse") throw new Error("SASL: Last message was not SASLResponse");
    if (typeof e != "string") throw new Error("SASL: SCRAM-SERVER-FINAL-MESSAGE: serverData must be a string");
    let { serverSignature: t } = Ku(
      e
    );
    if (t !== r.serverSignature) throw new Error("SASL: SCRAM-SERVER-FINAL-MESSAGE: server signature does not match");
  }
  __name(Gu, "Gu");
  a(Gu, "finalizeSession");
  function Vu(r) {
    if (typeof r != "string") throw new TypeError("SASL: text must be a string");
    return r.split("").map((e, t) => r.charCodeAt(t)).every((e) => e >= 33 && e <= 43 || e >= 45 && e <= 126);
  }
  __name(Vu, "Vu");
  a(Vu, "isPrintableChars");
  function ms(r) {
    return /^(?:[a-zA-Z0-9+/]{4})*(?:[a-zA-Z0-9+/]{2}==|[a-zA-Z0-9+/]{3}=)?$/.test(r);
  }
  __name(ms, "ms");
  a(ms, "isBase64");
  function gs(r) {
    if (typeof r != "string") throw new TypeError("SASL: attribute pairs text must be a string");
    return new Map(r.split(",").map((e) => {
      if (!/^.=/.test(e)) throw new Error("SASL: Invalid attribute pair entry");
      let t = e[0], n = e.substring(2);
      return [t, n];
    }));
  }
  __name(gs, "gs");
  a(gs, "parseAttributePairs");
  function zu(r) {
    let e = gs(r), t = e.get("r");
    if (t) {
      if (!Vu(t)) throw new Error("SASL: SCRAM-SERVER-FIRST-MESSAGE: nonce must only contain printable characters");
    } else throw new Error("SASL: SCRAM-SERVER-FIRST-MESSAGE: nonce missing");
    let n = e.get("s");
    if (n) {
      if (!ms(n)) throw new Error("SASL: SCRAM-SERVER-FIRST-MESSAGE: salt must be base64");
    } else throw new Error("SASL: SCRAM-SERVER-FIRST-MESSAGE: salt missing");
    let i = e.get("i");
    if (i) {
      if (!/^[1-9][0-9]*$/.test(i)) throw new Error("SASL: SCRAM-SERVER-FIRST-MESSAGE: invalid iteration count");
    } else throw new Error("SASL: SCRAM-SERVER-FIRST-MESSAGE: iteration missing");
    let s = parseInt(i, 10);
    return { nonce: t, salt: n, iteration: s };
  }
  __name(zu, "zu");
  a(zu, "parseServerFirstMessage");
  function Ku(r) {
    let t = gs(r).get("v");
    if (t) {
      if (!ms(t)) throw new Error("SASL: SCRAM-SERVER-FINAL-MESSAGE: server signature must be base64");
    } else throw new Error("SASL: SCRAM-SERVER-FINAL-MESSAGE: server signature is missing");
    return { serverSignature: t };
  }
  __name(Ku, "Ku");
  a(Ku, "parseServerFinalMessage");
  function ws(r, e) {
    if (!p.isBuffer(r)) throw new TypeError("first argument must be a Buffer");
    if (!p.isBuffer(e)) throw new TypeError(
      "second argument must be a Buffer"
    );
    if (r.length !== e.length) throw new Error("Buffer lengths must match");
    if (r.length === 0) throw new Error("Buffers cannot be empty");
    return p.from(r.map((t, n) => r[n] ^ e[n]));
  }
  __name(ws, "ws");
  a(ws, "xorBuffers");
  function Yu(r) {
    return pr.createHash("sha256").update(r).digest();
  }
  __name(Yu, "Yu");
  a(Yu, "sha256");
  function Oe(r, e) {
    return pr.createHmac("sha256", r).update(e).digest();
  }
  __name(Oe, "Oe");
  a(Oe, "hmacSha256");
  function Zu(r, e, t) {
    for (var n = Oe(
      r,
      p.concat([e, p.from([0, 0, 0, 1])])
    ), i = n, s = 0; s < t - 1; s++) n = Oe(r, n), i = ws(i, n);
    return i;
  }
  __name(Zu, "Zu");
  a(Zu, "Hi");
  bs.exports = { startSession: Hu, continueSession: $u, finalizeSession: Gu };
});
var yr = {};
se(yr, { join: /* @__PURE__ */ __name(() => Ju, "join") });
function Ju(...r) {
  return r.join("/");
}
__name(Ju, "Ju");
var mr = V(() => {
  "use strict";
  h();
  a(
    Ju,
    "join"
  );
});
var gr = {};
se(gr, { stat: /* @__PURE__ */ __name(() => Xu, "stat") });
function Xu(r, e) {
  e(new Error("No filesystem"));
}
__name(Xu, "Xu");
var wr = V(() => {
  "use strict";
  h();
  a(Xu, "stat");
});
var br = {};
se(br, { default: /* @__PURE__ */ __name(() => ec, "default") });
var ec;
var xr = V(() => {
  "use strict";
  h();
  ec = {};
});
var vs = {};
se(vs, { StringDecoder: /* @__PURE__ */ __name(() => vr, "StringDecoder") });
var Sr;
var vr;
var Ss = V(() => {
  "use strict";
  h();
  Sr = class Sr {
    static {
      __name(this, "Sr");
    }
    constructor(e) {
      E(this, "td");
      this.td = new TextDecoder(e);
    }
    write(e) {
      return this.td.decode(e, { stream: true });
    }
    end(e) {
      return this.td.decode(e);
    }
  };
  a(Sr, "StringDecoder");
  vr = Sr;
});
var _s = T((Kh, Cs) => {
  "use strict";
  h();
  var { Transform: tc } = (xr(), O(br)), { StringDecoder: rc } = (Ss(), O(vs)), Se = /* @__PURE__ */ Symbol(
    "last"
  ), It = /* @__PURE__ */ Symbol("decoder");
  function nc(r, e, t) {
    let n;
    if (this.overflow) {
      if (n = this[It].write(r).split(
        this.matcher
      ), n.length === 1) return t();
      n.shift(), this.overflow = false;
    } else this[Se] += this[It].write(r), n = this[Se].split(this.matcher);
    this[Se] = n.pop();
    for (let i = 0; i < n.length; i++) try {
      As(this, this.mapper(n[i]));
    } catch (s) {
      return t(s);
    }
    if (this.overflow = this[Se].length > this.maxLength, this.overflow && !this.skipOverflow) {
      t(new Error(
        "maximum buffer reached"
      ));
      return;
    }
    t();
  }
  __name(nc, "nc");
  a(nc, "transform");
  function ic(r) {
    if (this[Se] += this[It].end(), this[Se])
      try {
        As(this, this.mapper(this[Se]));
      } catch (e) {
        return r(e);
      }
    r();
  }
  __name(ic, "ic");
  a(ic, "flush");
  function As(r, e) {
    e !== void 0 && r.push(e);
  }
  __name(As, "As");
  a(As, "push");
  function Es(r) {
    return r;
  }
  __name(Es, "Es");
  a(Es, "noop");
  function sc(r, e, t) {
    switch (r = r || /\r?\n/, e = e || Es, t = t || {}, arguments.length) {
      case 1:
        typeof r == "function" ? (e = r, r = /\r?\n/) : typeof r == "object" && !(r instanceof RegExp) && !r[Symbol.split] && (t = r, r = /\r?\n/);
        break;
      case 2:
        typeof r == "function" ? (t = e, e = r, r = /\r?\n/) : typeof e == "object" && (t = e, e = Es);
    }
    t = Object.assign({}, t), t.autoDestroy = true, t.transform = nc, t.flush = ic, t.readableObjectMode = true;
    let n = new tc(t);
    return n[Se] = "", n[It] = new rc("utf8"), n.matcher = r, n.mapper = e, n.maxLength = t.maxLength, n.skipOverflow = t.skipOverflow || false, n.overflow = false, n._destroy = function(i, s) {
      this._writableState.errorEmitted = false, s(i);
    }, n;
  }
  __name(sc, "sc");
  a(sc, "split");
  Cs.exports = sc;
});
var Ps = T((Jh, ye) => {
  "use strict";
  h();
  var Ts = (mr(), O(yr)), oc = (xr(), O(br)).Stream, ac = _s(), Is = (it(), O(nt)), uc = 5432, Pt = y.platform === "win32", st = y.stderr, cc = 56, lc = 7, fc = 61440, hc = 32768;
  function dc(r) {
    return (r & fc) == hc;
  }
  __name(dc, "dc");
  a(dc, "isRegFile");
  var Ue = ["host", "port", "database", "user", "password"], Er = Ue.length, pc = Ue[Er - 1];
  function Ar() {
    var r = st instanceof oc && st.writable === true;
    if (r) {
      var e = Array.prototype.slice.call(arguments).concat(`
`);
      st.write(Is.format.apply(Is, e));
    }
  }
  __name(Ar, "Ar");
  a(Ar, "warn");
  Object.defineProperty(ye.exports, "isWin", { get: a(function() {
    return Pt;
  }, "get"), set: a(function(r) {
    Pt = r;
  }, "set") });
  ye.exports.warnTo = function(r) {
    var e = st;
    return st = r, e;
  };
  ye.exports.getFileName = function(r) {
    var e = r || y.env, t = e.PGPASSFILE || (Pt ? Ts.join(e.APPDATA || "./", "postgresql", "pgpass.conf") : Ts.join(e.HOME || "./", ".pgpass"));
    return t;
  };
  ye.exports.usePgPass = function(r, e) {
    return Object.prototype.hasOwnProperty.call(y.env, "PGPASSWORD") ? false : Pt ? true : (e = e || "<unkn>", dc(r.mode) ? r.mode & (cc | lc) ? (Ar('WARNING: password file "%s" has group or world access; permissions should be u=rw (0600) or less', e), false) : true : (Ar('WARNING: password file "%s" is not a plain file', e), false));
  };
  var yc = ye.exports.match = function(r, e) {
    return Ue.slice(0, -1).reduce(function(t, n, i) {
      return i == 1 && Number(r[n] || uc) === Number(
        e[n]
      ) ? t && true : t && (e[n] === "*" || e[n] === r[n]);
    }, true);
  };
  ye.exports.getPassword = function(r, e, t) {
    var n, i = e.pipe(
      ac()
    );
    function s(c) {
      var l = mc(c);
      l && gc(l) && yc(r, l) && (n = l[pc], i.end());
    }
    __name(s, "s");
    a(s, "onLine");
    var o = a(function() {
      e.destroy(), t(n);
    }, "onEnd"), u = a(function(c) {
      e.destroy(), Ar("WARNING: error on reading file: %s", c), t(
        void 0
      );
    }, "onErr");
    e.on("error", u), i.on("data", s).on("end", o).on("error", u);
  };
  var mc = ye.exports.parseLine = function(r) {
    if (r.length < 11 || r.match(/^\s+#/)) return null;
    for (var e = "", t = "", n = 0, i = 0, s = 0, o = {}, u = false, c = a(
      function(f, m, g) {
        var w = r.substring(m, g);
        Object.hasOwnProperty.call(y.env, "PGPASS_NO_DEESCAPE") || (w = w.replace(/\\([:\\])/g, "$1")), o[Ue[f]] = w;
      },
      "addToObj"
    ), l = 0; l < r.length - 1; l += 1) {
      if (e = r.charAt(l + 1), t = r.charAt(
        l
      ), u = n == Er - 1, u) {
        c(n, i);
        break;
      }
      l >= 0 && e == ":" && t !== "\\" && (c(n, i, l + 1), i = l + 2, n += 1);
    }
    return o = Object.keys(o).length === Er ? o : null, o;
  }, gc = ye.exports.isValidEntry = function(r) {
    for (var e = { 0: function(o) {
      return o.length > 0;
    }, 1: function(o) {
      return o === "*" ? true : (o = Number(o), isFinite(o) && o > 0 && o < 9007199254740992 && Math.floor(o) === o);
    }, 2: function(o) {
      return o.length > 0;
    }, 3: function(o) {
      return o.length > 0;
    }, 4: function(o) {
      return o.length > 0;
    } }, t = 0; t < Ue.length; t += 1) {
      var n = e[t], i = r[Ue[t]] || "", s = n(i);
      if (!s) return false;
    }
    return true;
  };
});
var Ls = T((rd, Cr) => {
  "use strict";
  h();
  var td = (mr(), O(yr)), Rs = (wr(), O(gr)), Rt = Ps();
  Cr.exports = function(r, e) {
    var t = Rt.getFileName();
    Rs.stat(t, function(n, i) {
      if (n || !Rt.usePgPass(i, t)) return e(void 0);
      var s = Rs.createReadStream(
        t
      );
      Rt.getPassword(r, s, e);
    });
  };
  Cr.exports.warnTo = Rt.warnTo;
});
var Bs = {};
se(Bs, { default: /* @__PURE__ */ __name(() => wc, "default") });
var wc;
var Fs = V(() => {
  "use strict";
  h();
  wc = {};
});
var Ms = {};
se(Ms, { parse: /* @__PURE__ */ __name(() => bc, "parse") });
function bc(r, e = false) {
  let { protocol: t } = new URL(r), n = "http:" + r.substring(
    t.length
  ), { username: i, password: s, host: o, hostname: u, port: c, pathname: l, search: f, searchParams: m, hash: g } = new URL(
    n
  );
  s = decodeURIComponent(s), i = decodeURIComponent(i), l = decodeURIComponent(l);
  let w = i + ":" + s, S = e ? Object.fromEntries(m.entries()) : f;
  return {
    href: r,
    protocol: t,
    auth: w,
    username: i,
    password: s,
    host: o,
    hostname: u,
    port: c,
    pathname: l,
    search: f,
    query: S,
    hash: g
  };
}
__name(bc, "bc");
var ks = V(() => {
  "use strict";
  h();
  a(bc, "parse");
});
var Ir = T((ad, Os) => {
  "use strict";
  h();
  var xc = (ks(), O(Ms)), _r = (wr(), O(gr));
  function Tr(r) {
    if (r.charAt(0) === "/") {
      var t = r.split(" ");
      return { host: t[0], database: t[1] };
    }
    var e = xc.parse(/ |%[^a-f0-9]|%[a-f0-9][^a-f0-9]/i.test(r) ? encodeURI(r).replace(/\%25(\d\d)/g, "%$1") : r, true), t = e.query;
    for (var n in t) Array.isArray(t[n]) && (t[n] = t[n][t[n].length - 1]);
    var i = (e.auth || ":").split(":");
    if (t.user = i[0], t.password = i.splice(1).join(
      ":"
    ), t.port = e.port, e.protocol == "socket:") return t.host = decodeURI(e.pathname), t.database = e.query.db, t.client_encoding = e.query.encoding, t;
    t.host || (t.host = e.hostname);
    var s = e.pathname;
    if (!t.host && s && /^%2f/i.test(s)) {
      var o = s.split("/");
      t.host = decodeURIComponent(o[0]), s = o.splice(1).join("/");
    }
    switch (s && s.charAt(
      0
    ) === "/" && (s = s.slice(1) || null), t.database = s && decodeURI(s), (t.ssl === "true" || t.ssl === "1") && (t.ssl = true), t.ssl === "0" && (t.ssl = false), (t.sslcert || t.sslkey || t.sslrootcert || t.sslmode) && (t.ssl = {}), t.sslcert && (t.ssl.cert = _r.readFileSync(t.sslcert).toString()), t.sslkey && (t.ssl.key = _r.readFileSync(t.sslkey).toString()), t.sslrootcert && (t.ssl.ca = _r.readFileSync(t.sslrootcert).toString()), t.sslmode) {
      case "disable": {
        t.ssl = false;
        break;
      }
      case "prefer":
      case "require":
      case "verify-ca":
      case "verify-full":
        break;
      case "no-verify": {
        t.ssl.rejectUnauthorized = false;
        break;
      }
    }
    return t;
  }
  __name(Tr, "Tr");
  a(Tr, "parse");
  Os.exports = Tr;
  Tr.parse = Tr;
});
var Lt = T((ld, Ds) => {
  "use strict";
  h();
  var vc = (Fs(), O(Bs)), Qs = tt(), Us = Ir().parse, j = a(function(r, e, t) {
    return t === void 0 ? t = y.env["PG" + r.toUpperCase()] : t === false || (t = y.env[t]), e[r] || t || Qs[r];
  }, "val"), Sc = a(function() {
    switch (y.env.PGSSLMODE) {
      case "disable":
        return false;
      case "prefer":
      case "require":
      case "verify-ca":
      case "verify-full":
        return true;
      case "no-verify":
        return { rejectUnauthorized: false };
    }
    return Qs.ssl;
  }, "readSSLConfigFromEnvironment"), Qe = a(function(r) {
    return "'" + ("" + r).replace(/\\/g, "\\\\").replace(/'/g, "\\'") + "'";
  }, "quoteParamValue"), te = a(function(r, e, t) {
    var n = e[t];
    n != null && r.push(t + "=" + Qe(n));
  }, "add"), Rr = class Rr {
    static {
      __name(this, "Rr");
    }
    constructor(e) {
      e = typeof e == "string" ? Us(e) : e || {}, e.connectionString && (e = Object.assign({}, e, Us(e.connectionString))), this.user = j("user", e), this.database = j("database", e), this.database === void 0 && (this.database = this.user), this.port = parseInt(j("port", e), 10), this.host = j("host", e), Object.defineProperty(this, "password", {
        configurable: true,
        enumerable: false,
        writable: true,
        value: j("password", e)
      }), this.binary = j("binary", e), this.options = j("options", e), this.ssl = typeof e.ssl > "u" ? Sc() : e.ssl, typeof this.ssl == "string" && this.ssl === "true" && (this.ssl = true), this.ssl === "no-verify" && (this.ssl = { rejectUnauthorized: false }), this.ssl && this.ssl.key && Object.defineProperty(this.ssl, "key", { enumerable: false }), this.client_encoding = j("client_encoding", e), this.replication = j("replication", e), this.isDomainSocket = !(this.host || "").indexOf("/"), this.application_name = j("application_name", e, "PGAPPNAME"), this.fallback_application_name = j("fallback_application_name", e, false), this.statement_timeout = j("statement_timeout", e, false), this.lock_timeout = j("lock_timeout", e, false), this.idle_in_transaction_session_timeout = j("idle_in_transaction_session_timeout", e, false), this.query_timeout = j("query_timeout", e, false), e.connectionTimeoutMillis === void 0 ? this.connect_timeout = y.env.PGCONNECT_TIMEOUT || 0 : this.connect_timeout = Math.floor(e.connectionTimeoutMillis / 1e3), e.keepAlive === false ? this.keepalives = 0 : e.keepAlive === true && (this.keepalives = 1), typeof e.keepAliveInitialDelayMillis == "number" && (this.keepalives_idle = Math.floor(e.keepAliveInitialDelayMillis / 1e3));
    }
    getLibpqConnectionString(e) {
      var t = [];
      te(t, this, "user"), te(t, this, "password"), te(t, this, "port"), te(t, this, "application_name"), te(
        t,
        this,
        "fallback_application_name"
      ), te(t, this, "connect_timeout"), te(t, this, "options");
      var n = typeof this.ssl == "object" ? this.ssl : this.ssl ? { sslmode: this.ssl } : {};
      if (te(t, n, "sslmode"), te(t, n, "sslca"), te(t, n, "sslkey"), te(t, n, "sslcert"), te(t, n, "sslrootcert"), this.database && t.push("dbname=" + Qe(this.database)), this.replication && t.push("replication=" + Qe(this.replication)), this.host && t.push("host=" + Qe(this.host)), this.isDomainSocket) return e(null, t.join(" "));
      this.client_encoding && t.push("client_encoding=" + Qe(this.client_encoding)), vc.lookup(this.host, function(i, s) {
        return i ? e(i, null) : (t.push("hostaddr=" + Qe(s)), e(null, t.join(" ")));
      });
    }
  };
  a(Rr, "ConnectionParameters");
  var Pr = Rr;
  Ds.exports = Pr;
});
var Ws = T((dd, Ns) => {
  "use strict";
  h();
  var Ec = Je(), qs = /^([A-Za-z]+)(?: (\d+))?(?: (\d+))?/, Br = class Br {
    static {
      __name(this, "Br");
    }
    constructor(e, t) {
      this.command = null, this.rowCount = null, this.oid = null, this.rows = [], this.fields = [], this._parsers = void 0, this._types = t, this.RowCtor = null, this.rowAsArray = e === "array", this.rowAsArray && (this.parseRow = this._parseRowAsArray);
    }
    addCommandComplete(e) {
      var t;
      e.text ? t = qs.exec(e.text) : t = qs.exec(e.command), t && (this.command = t[1], t[3] ? (this.oid = parseInt(
        t[2],
        10
      ), this.rowCount = parseInt(t[3], 10)) : t[2] && (this.rowCount = parseInt(t[2], 10)));
    }
    _parseRowAsArray(e) {
      for (var t = new Array(
        e.length
      ), n = 0, i = e.length; n < i; n++) {
        var s = e[n];
        s !== null ? t[n] = this._parsers[n](s) : t[n] = null;
      }
      return t;
    }
    parseRow(e) {
      for (var t = {}, n = 0, i = e.length; n < i; n++) {
        var s = e[n], o = this.fields[n].name;
        s !== null ? t[o] = this._parsers[n](
          s
        ) : t[o] = null;
      }
      return t;
    }
    addRow(e) {
      this.rows.push(e);
    }
    addFields(e) {
      this.fields = e, this.fields.length && (this._parsers = new Array(e.length));
      for (var t = 0; t < e.length; t++) {
        var n = e[t];
        this._types ? this._parsers[t] = this._types.getTypeParser(n.dataTypeID, n.format || "text") : this._parsers[t] = Ec.getTypeParser(n.dataTypeID, n.format || "text");
      }
    }
  };
  a(Br, "Result");
  var Lr = Br;
  Ns.exports = Lr;
});
var Gs = T((md, $s) => {
  "use strict";
  h();
  var { EventEmitter: Ac } = ve(), js = Ws(), Hs = rt(), Mr = class Mr extends Ac {
    static {
      __name(this, "Mr");
    }
    constructor(e, t, n) {
      super(), e = Hs.normalizeQueryConfig(e, t, n), this.text = e.text, this.values = e.values, this.rows = e.rows, this.types = e.types, this.name = e.name, this.binary = e.binary, this.portal = e.portal || "", this.callback = e.callback, this._rowMode = e.rowMode, y.domain && e.callback && (this.callback = y.domain.bind(e.callback)), this._result = new js(this._rowMode, this.types), this._results = this._result, this.isPreparedStatement = false, this._canceledDueToError = false, this._promise = null;
    }
    requiresPreparation() {
      return this.name || this.rows ? true : !this.text || !this.values ? false : this.values.length > 0;
    }
    _checkForMultirow() {
      this._result.command && (Array.isArray(this._results) || (this._results = [this._result]), this._result = new js(this._rowMode, this.types), this._results.push(this._result));
    }
    handleRowDescription(e) {
      this._checkForMultirow(), this._result.addFields(e.fields), this._accumulateRows = this.callback || !this.listeners("row").length;
    }
    handleDataRow(e) {
      let t;
      if (!this._canceledDueToError) {
        try {
          t = this._result.parseRow(
            e.fields
          );
        } catch (n) {
          this._canceledDueToError = n;
          return;
        }
        this.emit("row", t, this._result), this._accumulateRows && this._result.addRow(t);
      }
    }
    handleCommandComplete(e, t) {
      this._checkForMultirow(), this._result.addCommandComplete(
        e
      ), this.rows && t.sync();
    }
    handleEmptyQuery(e) {
      this.rows && e.sync();
    }
    handleError(e, t) {
      if (this._canceledDueToError && (e = this._canceledDueToError, this._canceledDueToError = false), this.callback) return this.callback(e);
      this.emit("error", e);
    }
    handleReadyForQuery(e) {
      if (this._canceledDueToError) return this.handleError(
        this._canceledDueToError,
        e
      );
      if (this.callback) try {
        this.callback(null, this._results);
      } catch (t) {
        y.nextTick(() => {
          throw t;
        });
      }
      this.emit(
        "end",
        this._results
      );
    }
    submit(e) {
      if (typeof this.text != "string" && typeof this.name != "string") return new Error(
        "A query must have either text or a name. Supplying neither is unsupported."
      );
      let t = e.parsedStatements[this.name];
      return this.text && t && this.text !== t ? new Error(`Prepared statements must be unique - '${this.name}' was used for a different statement`) : this.values && !Array.isArray(this.values) ? new Error("Query values must be an array") : (this.requiresPreparation() ? this.prepare(e) : e.query(this.text), null);
    }
    hasBeenParsed(e) {
      return this.name && e.parsedStatements[this.name];
    }
    handlePortalSuspended(e) {
      this._getRows(e, this.rows);
    }
    _getRows(e, t) {
      e.execute({ portal: this.portal, rows: t }), t ? e.flush() : e.sync();
    }
    prepare(e) {
      this.isPreparedStatement = true, this.hasBeenParsed(e) || e.parse({ text: this.text, name: this.name, types: this.types });
      try {
        e.bind({ portal: this.portal, statement: this.name, values: this.values, binary: this.binary, valueMapper: Hs.prepareValue });
      } catch (t) {
        this.handleError(t, e);
        return;
      }
      e.describe({ type: "P", name: this.portal || "" }), this._getRows(e, this.rows);
    }
    handleCopyInResponse(e) {
      e.sendCopyFail("No source stream defined");
    }
    handleCopyData(e, t) {
    }
  };
  a(Mr, "Query");
  var Fr = Mr;
  $s.exports = Fr;
});
var ln = T((_) => {
  "use strict";
  h();
  Object.defineProperty(_, "__esModule", { value: true });
  _.NoticeMessage = _.DataRowMessage = _.CommandCompleteMessage = _.ReadyForQueryMessage = _.NotificationResponseMessage = _.BackendKeyDataMessage = _.AuthenticationMD5Password = _.ParameterStatusMessage = _.ParameterDescriptionMessage = _.RowDescriptionMessage = _.Field = _.CopyResponse = _.CopyDataMessage = _.DatabaseError = _.copyDone = _.emptyQuery = _.replicationStart = _.portalSuspended = _.noData = _.closeComplete = _.bindComplete = _.parseComplete = void 0;
  _.parseComplete = { name: "parseComplete", length: 5 };
  _.bindComplete = { name: "bindComplete", length: 5 };
  _.closeComplete = { name: "closeComplete", length: 5 };
  _.noData = { name: "noData", length: 5 };
  _.portalSuspended = { name: "portalSuspended", length: 5 };
  _.replicationStart = { name: "replicationStart", length: 4 };
  _.emptyQuery = { name: "emptyQuery", length: 4 };
  _.copyDone = { name: "copyDone", length: 4 };
  var Kr = class Kr extends Error {
    static {
      __name(this, "Kr");
    }
    constructor(e, t, n) {
      super(e), this.length = t, this.name = n;
    }
  };
  a(Kr, "DatabaseError");
  var kr = Kr;
  _.DatabaseError = kr;
  var Yr = class Yr {
    static {
      __name(this, "Yr");
    }
    constructor(e, t) {
      this.length = e, this.chunk = t, this.name = "copyData";
    }
  };
  a(Yr, "CopyDataMessage");
  var Or = Yr;
  _.CopyDataMessage = Or;
  var Zr = class Zr {
    static {
      __name(this, "Zr");
    }
    constructor(e, t, n, i) {
      this.length = e, this.name = t, this.binary = n, this.columnTypes = new Array(i);
    }
  };
  a(Zr, "CopyResponse");
  var Ur = Zr;
  _.CopyResponse = Ur;
  var Jr = class Jr {
    static {
      __name(this, "Jr");
    }
    constructor(e, t, n, i, s, o, u) {
      this.name = e, this.tableID = t, this.columnID = n, this.dataTypeID = i, this.dataTypeSize = s, this.dataTypeModifier = o, this.format = u;
    }
  };
  a(Jr, "Field");
  var Qr = Jr;
  _.Field = Qr;
  var Xr = class Xr {
    static {
      __name(this, "Xr");
    }
    constructor(e, t) {
      this.length = e, this.fieldCount = t, this.name = "rowDescription", this.fields = new Array(this.fieldCount);
    }
  };
  a(Xr, "RowDescriptionMessage");
  var Dr = Xr;
  _.RowDescriptionMessage = Dr;
  var en = class en {
    static {
      __name(this, "en");
    }
    constructor(e, t) {
      this.length = e, this.parameterCount = t, this.name = "parameterDescription", this.dataTypeIDs = new Array(this.parameterCount);
    }
  };
  a(en, "ParameterDescriptionMessage");
  var qr = en;
  _.ParameterDescriptionMessage = qr;
  var tn = class tn {
    static {
      __name(this, "tn");
    }
    constructor(e, t, n) {
      this.length = e, this.parameterName = t, this.parameterValue = n, this.name = "parameterStatus";
    }
  };
  a(tn, "ParameterStatusMessage");
  var Nr = tn;
  _.ParameterStatusMessage = Nr;
  var rn = class rn {
    static {
      __name(this, "rn");
    }
    constructor(e, t) {
      this.length = e, this.salt = t, this.name = "authenticationMD5Password";
    }
  };
  a(rn, "AuthenticationMD5Password");
  var Wr = rn;
  _.AuthenticationMD5Password = Wr;
  var nn = class nn {
    static {
      __name(this, "nn");
    }
    constructor(e, t, n) {
      this.length = e, this.processID = t, this.secretKey = n, this.name = "backendKeyData";
    }
  };
  a(nn, "BackendKeyDataMessage");
  var jr = nn;
  _.BackendKeyDataMessage = jr;
  var sn = class sn {
    static {
      __name(this, "sn");
    }
    constructor(e, t, n, i) {
      this.length = e, this.processId = t, this.channel = n, this.payload = i, this.name = "notification";
    }
  };
  a(sn, "NotificationResponseMessage");
  var Hr = sn;
  _.NotificationResponseMessage = Hr;
  var on = class on {
    static {
      __name(this, "on");
    }
    constructor(e, t) {
      this.length = e, this.status = t, this.name = "readyForQuery";
    }
  };
  a(on, "ReadyForQueryMessage");
  var $r = on;
  _.ReadyForQueryMessage = $r;
  var an = class an {
    static {
      __name(this, "an");
    }
    constructor(e, t) {
      this.length = e, this.text = t, this.name = "commandComplete";
    }
  };
  a(an, "CommandCompleteMessage");
  var Gr = an;
  _.CommandCompleteMessage = Gr;
  var un = class un {
    static {
      __name(this, "un");
    }
    constructor(e, t) {
      this.length = e, this.fields = t, this.name = "dataRow", this.fieldCount = t.length;
    }
  };
  a(un, "DataRowMessage");
  var Vr = un;
  _.DataRowMessage = Vr;
  var cn = class cn {
    static {
      __name(this, "cn");
    }
    constructor(e, t) {
      this.length = e, this.message = t, this.name = "notice";
    }
  };
  a(cn, "NoticeMessage");
  var zr = cn;
  _.NoticeMessage = zr;
});
var Vs = T((Bt) => {
  "use strict";
  h();
  Object.defineProperty(Bt, "__esModule", { value: true });
  Bt.Writer = void 0;
  var hn = class hn {
    static {
      __name(this, "hn");
    }
    constructor(e = 256) {
      this.size = e, this.offset = 5, this.headerPosition = 0, this.buffer = p.allocUnsafe(e);
    }
    ensure(e) {
      if (this.buffer.length - this.offset < e) {
        let n = this.buffer, i = n.length + (n.length >> 1) + e;
        this.buffer = p.allocUnsafe(i), n.copy(
          this.buffer
        );
      }
    }
    addInt32(e) {
      return this.ensure(4), this.buffer[this.offset++] = e >>> 24 & 255, this.buffer[this.offset++] = e >>> 16 & 255, this.buffer[this.offset++] = e >>> 8 & 255, this.buffer[this.offset++] = e >>> 0 & 255, this;
    }
    addInt16(e) {
      return this.ensure(2), this.buffer[this.offset++] = e >>> 8 & 255, this.buffer[this.offset++] = e >>> 0 & 255, this;
    }
    addCString(e) {
      if (!e) this.ensure(1);
      else {
        let t = p.byteLength(e);
        this.ensure(t + 1), this.buffer.write(e, this.offset, "utf-8"), this.offset += t;
      }
      return this.buffer[this.offset++] = 0, this;
    }
    addString(e = "") {
      let t = p.byteLength(e);
      return this.ensure(t), this.buffer.write(e, this.offset), this.offset += t, this;
    }
    addInt32PrefixedString(e) {
      let t = p.byteLength(e);
      this.ensure(4 + t);
      let n = this.buffer, i = this.offset;
      return n[i++] = t >>> 24 & 255, n[i++] = t >>> 16 & 255, n[i++] = t >>> 8 & 255, n[i++] = t >>> 0 & 255, n.write(e, i, "utf-8"), this.offset = i + t, this;
    }
    add(e) {
      return this.ensure(e.length), e.copy(this.buffer, this.offset), this.offset += e.length, this;
    }
    join(e) {
      if (e) {
        this.buffer[this.headerPosition] = e;
        let t = this.offset - (this.headerPosition + 1);
        this.buffer.writeInt32BE(t, this.headerPosition + 1);
      }
      return this.buffer.slice(e ? 0 : 5, this.offset);
    }
    flush(e) {
      let t = this.join(e);
      return this.offset = 5, this.headerPosition = 0, this.buffer = p.allocUnsafe(this.size), t;
    }
    clear() {
      this.offset = 5, this.headerPosition = 0;
    }
  };
  a(hn, "Writer");
  var fn = hn;
  Bt.Writer = fn;
});
var Ks = T((Mt) => {
  "use strict";
  h();
  Object.defineProperty(Mt, "__esModule", { value: true });
  Mt.serialize = void 0;
  var dn = Vs(), L = new dn.Writer(), Cc = a((r) => {
    L.addInt16(3).addInt16(0);
    for (let n of Object.keys(r)) L.addCString(
      n
    ).addCString(r[n]);
    L.addCString("client_encoding").addCString("UTF8");
    let e = L.addCString("").flush(), t = e.length + 4;
    return new dn.Writer().addInt32(t).add(e).flush();
  }, "startup"), _c = a(() => {
    let r = p.allocUnsafe(
      8
    );
    return r.writeInt32BE(8, 0), r.writeInt32BE(80877103, 4), r;
  }, "requestSsl"), Tc = a((r) => L.addCString(r).flush(
    112
  ), "password"), Ic = a(function(r, e) {
    return L.addCString(r).addInt32PrefixedString(e), L.flush(112);
  }, "sendSASLInitialResponseMessage"), Pc = a(function(r) {
    return L.addString(r).flush(112);
  }, "sendSCRAMClientFinalMessage"), Rc = a((r) => L.addCString(r).flush(81), "query"), zs = [], Lc = a((r) => {
    let e = r.name || "";
    e.length > 63 && (console.error("Warning! Postgres only supports 63 characters for query names."), console.error("You supplied %s (%s)", e, e.length), console.error("This can cause conflicts and silent errors executing queries"));
    let t = r.types || zs, n = t.length, i = L.addCString(e).addCString(r.text).addInt16(n);
    for (let s = 0; s < n; s++) i.addInt32(t[s]);
    return L.flush(80);
  }, "parse"), De = new dn.Writer(), Bc = a(function(r, e) {
    for (let t = 0; t < r.length; t++) {
      let n = e ? e(r[t], t) : r[t];
      n == null ? (L.addInt16(0), De.addInt32(-1)) : n instanceof p ? (L.addInt16(
        1
      ), De.addInt32(n.length), De.add(n)) : (L.addInt16(0), De.addInt32PrefixedString(n));
    }
  }, "writeValues"), Fc = a(
    (r = {}) => {
      let e = r.portal || "", t = r.statement || "", n = r.binary || false, i = r.values || zs, s = i.length;
      L.addCString(
        e
      ).addCString(t), L.addInt16(s);
      try {
        Bc(i, r.valueMapper);
      } catch (o) {
        throw L.clear(), De.clear(), o;
      }
      return L.addInt16(s), L.add(De.flush()), L.addInt16(1), L.addInt16(n ? 1 : 0), L.flush(66);
    },
    "bind"
  ), Mc = p.from([
    69,
    0,
    0,
    0,
    9,
    0,
    0,
    0,
    0,
    0
  ]), kc = a((r) => {
    if (!r || !r.portal && !r.rows) return Mc;
    let e = r.portal || "", t = r.rows || 0, n = p.byteLength(
      e
    ), i = 4 + n + 1 + 4, s = p.allocUnsafe(1 + i);
    return s[0] = 69, s.writeInt32BE(i, 1), s.write(e, 5, "utf-8"), s[n + 5] = 0, s.writeUInt32BE(t, s.length - 4), s;
  }, "execute"), Oc = a((r, e) => {
    let t = p.allocUnsafe(16);
    return t.writeInt32BE(
      16,
      0
    ), t.writeInt16BE(1234, 4), t.writeInt16BE(5678, 6), t.writeInt32BE(r, 8), t.writeInt32BE(e, 12), t;
  }, "cancel"), pn = a((r, e) => {
    let n = 4 + p.byteLength(e) + 1, i = p.allocUnsafe(1 + n);
    return i[0] = r, i.writeInt32BE(n, 1), i.write(e, 5, "utf-8"), i[n] = 0, i;
  }, "cstringMessage"), Uc = L.addCString("P").flush(68), Qc = L.addCString("S").flush(68), Dc = a((r) => r.name ? pn(68, `${r.type}${r.name || ""}`) : r.type === "P" ? Uc : Qc, "describe"), qc = a((r) => {
    let e = `${r.type}${r.name || ""}`;
    return pn(67, e);
  }, "close"), Nc = a((r) => L.add(r).flush(100), "copyData"), Wc = a((r) => pn(
    102,
    r
  ), "copyFail"), Ft = a((r) => p.from([r, 0, 0, 0, 4]), "codeOnlyBuffer"), jc = Ft(72), Hc = Ft(83), $c = Ft(88), Gc = Ft(99), Vc = {
    startup: Cc,
    password: Tc,
    requestSsl: _c,
    sendSASLInitialResponseMessage: Ic,
    sendSCRAMClientFinalMessage: Pc,
    query: Rc,
    parse: Lc,
    bind: Fc,
    execute: kc,
    describe: Dc,
    close: qc,
    flush: a(() => jc, "flush"),
    sync: a(() => Hc, "sync"),
    end: a(() => $c, "end"),
    copyData: Nc,
    copyDone: a(() => Gc, "copyDone"),
    copyFail: Wc,
    cancel: Oc
  };
  Mt.serialize = Vc;
});
var Ys = T((kt) => {
  "use strict";
  h();
  Object.defineProperty(kt, "__esModule", { value: true });
  kt.BufferReader = void 0;
  var mn = class mn {
    static {
      __name(this, "mn");
    }
    constructor(e = 0) {
      this.offset = e, this.buffer = p.allocUnsafe(0), this.encoding = "utf-8";
    }
    setBuffer(e, t) {
      this.offset = e, this.buffer = t;
    }
    int16() {
      let e = this.buffer.readInt16BE(this.offset);
      return this.offset += 2, e;
    }
    byte() {
      let e = this.buffer[this.offset];
      return this.offset++, e;
    }
    int32() {
      let e = this.buffer.readInt32BE(
        this.offset
      );
      return this.offset += 4, e;
    }
    uint32() {
      let e = this.buffer.readUInt32BE(this.offset);
      return this.offset += 4, e;
    }
    string(e) {
      let t = this.buffer.toString(this.encoding, this.offset, this.offset + e);
      return this.offset += e, t;
    }
    cstring() {
      let e = this.offset, t = e;
      for (; this.buffer[t++]; ) ;
      return this.offset = t, this.buffer.toString(this.encoding, e, t - 1);
    }
    bytes(e) {
      let t = this.buffer.slice(this.offset, this.offset + e);
      return this.offset += e, t;
    }
  };
  a(mn, "BufferReader");
  var yn = mn;
  kt.BufferReader = yn;
});
var eo = T((Ot) => {
  "use strict";
  h();
  Object.defineProperty(Ot, "__esModule", { value: true });
  Ot.Parser = void 0;
  var F = ln(), zc = Ys(), wn = 1, Kc = 4, Zs = wn + Kc, Z = -1, gn = p.allocUnsafe(0), xn = class xn {
    static {
      __name(this, "xn");
    }
    constructor(e) {
      if (this.buffer = gn, this.bufferLength = 0, this.bufferOffset = 0, this.reader = new zc.BufferReader(), e?.mode === "binary") throw new Error(
        "Binary mode not supported yet"
      );
      this.mode = e?.mode || "text";
    }
    parse(e, t) {
      this.mergeBuffer(e);
      let n = this.bufferOffset + this.bufferLength, i = this.bufferOffset;
      for (; i + Zs <= n; ) {
        let s = this.buffer[i], o = this.buffer.readUInt32BE(i + wn), u = wn + o;
        if (u + i <= n) {
          let c = this.handlePacket(i + Zs, s, o, this.buffer);
          t(c), i += u;
        } else break;
      }
      i === n ? (this.buffer = gn, this.bufferLength = 0, this.bufferOffset = 0) : (this.bufferLength = n - i, this.bufferOffset = i);
    }
    mergeBuffer(e) {
      if (this.bufferLength > 0) {
        let t = this.bufferLength + e.byteLength;
        if (t + this.bufferOffset > this.buffer.byteLength) {
          let i;
          if (t <= this.buffer.byteLength && this.bufferOffset >= this.bufferLength) i = this.buffer;
          else {
            let s = this.buffer.byteLength * 2;
            for (; t >= s; ) s *= 2;
            i = p.allocUnsafe(s);
          }
          this.buffer.copy(i, 0, this.bufferOffset, this.bufferOffset + this.bufferLength), this.buffer = i, this.bufferOffset = 0;
        }
        e.copy(
          this.buffer,
          this.bufferOffset + this.bufferLength
        ), this.bufferLength = t;
      } else this.buffer = e, this.bufferOffset = 0, this.bufferLength = e.byteLength;
    }
    handlePacket(e, t, n, i) {
      let { reader: s } = this;
      s.setBuffer(e, i);
      let o;
      switch (t) {
        case 50:
          o = F.bindComplete;
          break;
        case 49:
          o = F.parseComplete;
          break;
        case 51:
          o = F.closeComplete;
          break;
        case 110:
          o = F.noData;
          break;
        case 115:
          o = F.portalSuspended;
          break;
        case 99:
          o = F.copyDone;
          break;
        case 87:
          o = F.replicationStart;
          break;
        case 73:
          o = F.emptyQuery;
          break;
        case 68:
          o = sl(s);
          break;
        case 67:
          o = Zc(s);
          break;
        case 90:
          o = Yc(s);
          break;
        case 65:
          o = tl(s);
          break;
        case 82:
          o = ul(s, n);
          break;
        case 83:
          o = ol(s);
          break;
        case 75:
          o = al(s);
          break;
        case 69:
          o = Js(s, "error");
          break;
        case 78:
          o = Js(s, "notice");
          break;
        case 84:
          o = rl(s);
          break;
        case 116:
          o = il(s);
          break;
        case 71:
          o = Xc(
            s
          );
          break;
        case 72:
          o = el(s);
          break;
        case 100:
          o = Jc(s, n);
          break;
        default:
          return new F.DatabaseError("received invalid response: " + t.toString(16), n, "error");
      }
      return s.setBuffer(0, gn), o.length = n, o;
    }
  };
  a(xn, "Parser");
  var bn = xn;
  Ot.Parser = bn;
  var Yc = a((r) => {
    let e = r.string(1);
    return new F.ReadyForQueryMessage(Z, e);
  }, "parseReadyForQueryMessage"), Zc = a((r) => {
    let e = r.cstring();
    return new F.CommandCompleteMessage(Z, e);
  }, "parseCommandCompleteMessage"), Jc = a((r, e) => {
    let t = r.bytes(e - 4);
    return new F.CopyDataMessage(Z, t);
  }, "parseCopyData"), Xc = a((r) => Xs(r, "copyInResponse"), "parseCopyInMessage"), el = a((r) => Xs(r, "copyOutResponse"), "parseCopyOutMessage"), Xs = a((r, e) => {
    let t = r.byte() !== 0, n = r.int16(), i = new F.CopyResponse(Z, e, t, n);
    for (let s = 0; s < n; s++) i.columnTypes[s] = r.int16();
    return i;
  }, "parseCopyMessage"), tl = a((r) => {
    let e = r.int32(), t = r.cstring(), n = r.cstring();
    return new F.NotificationResponseMessage(Z, e, t, n);
  }, "parseNotificationMessage"), rl = a((r) => {
    let e = r.int16(), t = new F.RowDescriptionMessage(Z, e);
    for (let n = 0; n < e; n++) t.fields[n] = nl(r);
    return t;
  }, "parseRowDescriptionMessage"), nl = a((r) => {
    let e = r.cstring(), t = r.uint32(), n = r.int16(), i = r.uint32(), s = r.int16(), o = r.int32(), u = r.int16() === 0 ? "text" : "binary";
    return new F.Field(e, t, n, i, s, o, u);
  }, "parseField"), il = a((r) => {
    let e = r.int16(), t = new F.ParameterDescriptionMessage(Z, e);
    for (let n = 0; n < e; n++) t.dataTypeIDs[n] = r.uint32();
    return t;
  }, "parseParameterDescriptionMessage"), sl = a((r) => {
    let e = r.int16(), t = new Array(e);
    for (let n = 0; n < e; n++) {
      let i = r.int32();
      t[n] = i === -1 ? null : r.string(i);
    }
    return new F.DataRowMessage(Z, t);
  }, "parseDataRowMessage"), ol = a((r) => {
    let e = r.cstring(), t = r.cstring();
    return new F.ParameterStatusMessage(Z, e, t);
  }, "parseParameterStatusMessage"), al = a((r) => {
    let e = r.int32(), t = r.int32();
    return new F.BackendKeyDataMessage(
      Z,
      e,
      t
    );
  }, "parseBackendKeyData"), ul = a((r, e) => {
    let t = r.int32(), n = { name: "authenticationOk", length: e };
    switch (t) {
      case 0:
        break;
      case 3:
        n.length === 8 && (n.name = "authenticationCleartextPassword");
        break;
      case 5:
        if (n.length === 12) {
          n.name = "authenticationMD5Password";
          let i = r.bytes(4);
          return new F.AuthenticationMD5Password(Z, i);
        }
        break;
      case 10:
        {
          n.name = "authenticationSASL", n.mechanisms = [];
          let i;
          do
            i = r.cstring(), i && n.mechanisms.push(i);
          while (i);
        }
        break;
      case 11:
        n.name = "authenticationSASLContinue", n.data = r.string(e - 8);
        break;
      case 12:
        n.name = "authenticationSASLFinal", n.data = r.string(e - 8);
        break;
      default:
        throw new Error("Unknown authenticationOk message type " + t);
    }
    return n;
  }, "parseAuthenticationResponse"), Js = a((r, e) => {
    let t = {}, n = r.string(1);
    for (; n !== "\0"; ) t[n] = r.cstring(), n = r.string(1);
    let i = t.M, s = e === "notice" ? new F.NoticeMessage(Z, i) : new F.DatabaseError(
      i,
      Z,
      e
    );
    return s.severity = t.S, s.code = t.C, s.detail = t.D, s.hint = t.H, s.position = t.P, s.internalPosition = t.p, s.internalQuery = t.q, s.where = t.W, s.schema = t.s, s.table = t.t, s.column = t.c, s.dataType = t.d, s.constraint = t.n, s.file = t.F, s.line = t.L, s.routine = t.R, s;
  }, "parseErrorMessage");
});
var vn = T((_e) => {
  "use strict";
  h();
  Object.defineProperty(_e, "__esModule", { value: true });
  _e.DatabaseError = _e.serialize = void 0;
  _e.parse = hl;
  var cl = ln();
  Object.defineProperty(_e, "DatabaseError", { enumerable: true, get: a(
    function() {
      return cl.DatabaseError;
    },
    "get"
  ) });
  var ll = Ks();
  Object.defineProperty(_e, "serialize", {
    enumerable: true,
    get: a(function() {
      return ll.serialize;
    }, "get")
  });
  var fl = eo();
  function hl(r, e) {
    let t = new fl.Parser();
    return r.on("data", (n) => t.parse(n, e)), new Promise((n) => r.on("end", () => n()));
  }
  __name(hl, "hl");
  a(hl, "parse");
});
var to = {};
se(to, { connect: /* @__PURE__ */ __name(() => dl, "connect") });
function dl({ socket: r, servername: e }) {
  return r.startTls(e), r;
}
__name(dl, "dl");
var ro = V(
  () => {
    "use strict";
    h();
    a(dl, "connect");
  }
);
var An = T((Dd, so) => {
  "use strict";
  h();
  var no = (Ge(), O(Ii)), pl = ve().EventEmitter, { parse: yl, serialize: Q } = vn(), io = Q.flush(), ml = Q.sync(), gl = Q.end(), En = class En extends pl {
    static {
      __name(this, "En");
    }
    constructor(e) {
      super(), e = e || {}, this.stream = e.stream || new no.Socket(), this._keepAlive = e.keepAlive, this._keepAliveInitialDelayMillis = e.keepAliveInitialDelayMillis, this.lastBuffer = false, this.parsedStatements = {}, this.ssl = e.ssl || false, this._ending = false, this._emitMessage = false;
      var t = this;
      this.on("newListener", function(n) {
        n === "message" && (t._emitMessage = true);
      });
    }
    connect(e, t) {
      var n = this;
      this._connecting = true, this.stream.setNoDelay(true), this.stream.connect(e, t), this.stream.once("connect", function() {
        n._keepAlive && n.stream.setKeepAlive(true, n._keepAliveInitialDelayMillis), n.emit("connect");
      });
      let i = a(function(s) {
        n._ending && (s.code === "ECONNRESET" || s.code === "EPIPE") || n.emit("error", s);
      }, "reportStreamError");
      if (this.stream.on("error", i), this.stream.on("close", function() {
        n.emit("end");
      }), !this.ssl) return this.attachListeners(
        this.stream
      );
      this.stream.once("data", function(s) {
        var o = s.toString("utf8");
        switch (o) {
          case "S":
            break;
          case "N":
            return n.stream.end(), n.emit("error", new Error("The server does not support SSL connections"));
          default:
            return n.stream.end(), n.emit("error", new Error("There was an error establishing an SSL connection"));
        }
        var u = (ro(), O(to));
        let c = { socket: n.stream };
        n.ssl !== true && (Object.assign(c, n.ssl), "key" in n.ssl && (c.key = n.ssl.key)), no.isIP(t) === 0 && (c.servername = t);
        try {
          n.stream = u.connect(c);
        } catch (l) {
          return n.emit(
            "error",
            l
          );
        }
        n.attachListeners(n.stream), n.stream.on("error", i), n.emit("sslconnect");
      });
    }
    attachListeners(e) {
      e.on(
        "end",
        () => {
          this.emit("end");
        }
      ), yl(e, (t) => {
        var n = t.name === "error" ? "errorMessage" : t.name;
        this._emitMessage && this.emit("message", t), this.emit(n, t);
      });
    }
    requestSsl() {
      this.stream.write(Q.requestSsl());
    }
    startup(e) {
      this.stream.write(Q.startup(e));
    }
    cancel(e, t) {
      this._send(Q.cancel(e, t));
    }
    password(e) {
      this._send(Q.password(e));
    }
    sendSASLInitialResponseMessage(e, t) {
      this._send(Q.sendSASLInitialResponseMessage(e, t));
    }
    sendSCRAMClientFinalMessage(e) {
      this._send(Q.sendSCRAMClientFinalMessage(
        e
      ));
    }
    _send(e) {
      return this.stream.writable ? this.stream.write(e) : false;
    }
    query(e) {
      this._send(Q.query(e));
    }
    parse(e) {
      this._send(Q.parse(e));
    }
    bind(e) {
      this._send(Q.bind(e));
    }
    execute(e) {
      this._send(Q.execute(e));
    }
    flush() {
      this.stream.writable && this.stream.write(io);
    }
    sync() {
      this._ending = true, this._send(io), this._send(ml);
    }
    ref() {
      this.stream.ref();
    }
    unref() {
      this.stream.unref();
    }
    end() {
      if (this._ending = true, !this._connecting || !this.stream.writable) {
        this.stream.end();
        return;
      }
      return this.stream.write(gl, () => {
        this.stream.end();
      });
    }
    close(e) {
      this._send(Q.close(e));
    }
    describe(e) {
      this._send(Q.describe(e));
    }
    sendCopyFromChunk(e) {
      this._send(Q.copyData(e));
    }
    endCopyFrom() {
      this._send(Q.copyDone());
    }
    sendCopyFail(e) {
      this._send(Q.copyFail(e));
    }
  };
  a(En, "Connection");
  var Sn = En;
  so.exports = Sn;
});
var uo = T((jd, ao) => {
  "use strict";
  h();
  var wl = ve().EventEmitter, Wd = (it(), O(nt)), bl = rt(), Cn = xs(), xl = Ls(), vl = _t(), Sl = Lt(), oo = Gs(), El = tt(), Al = An(), _n = class _n extends wl {
    static {
      __name(this, "_n");
    }
    constructor(e) {
      super(), this.connectionParameters = new Sl(e), this.user = this.connectionParameters.user, this.database = this.connectionParameters.database, this.port = this.connectionParameters.port, this.host = this.connectionParameters.host, Object.defineProperty(
        this,
        "password",
        { configurable: true, enumerable: false, writable: true, value: this.connectionParameters.password }
      ), this.replication = this.connectionParameters.replication;
      var t = e || {};
      this._Promise = t.Promise || b.Promise, this._types = new vl(t.types), this._ending = false, this._connecting = false, this._connected = false, this._connectionError = false, this._queryable = true, this.connection = t.connection || new Al({ stream: t.stream, ssl: this.connectionParameters.ssl, keepAlive: t.keepAlive || false, keepAliveInitialDelayMillis: t.keepAliveInitialDelayMillis || 0, encoding: this.connectionParameters.client_encoding || "utf8" }), this.queryQueue = [], this.binary = t.binary || El.binary, this.processID = null, this.secretKey = null, this.ssl = this.connectionParameters.ssl || false, this.ssl && this.ssl.key && Object.defineProperty(this.ssl, "key", { enumerable: false }), this._connectionTimeoutMillis = t.connectionTimeoutMillis || 0;
    }
    _errorAllQueries(e) {
      let t = a((n) => {
        y.nextTick(() => {
          n.handleError(e, this.connection);
        });
      }, "enqueueError");
      this.activeQuery && (t(this.activeQuery), this.activeQuery = null), this.queryQueue.forEach(t), this.queryQueue.length = 0;
    }
    _connect(e) {
      var t = this, n = this.connection;
      if (this._connectionCallback = e, this._connecting || this._connected) {
        let i = new Error("Client has already been connected. You cannot reuse a client.");
        y.nextTick(
          () => {
            e(i);
          }
        );
        return;
      }
      this._connecting = true, this.connectionTimeoutHandle, this._connectionTimeoutMillis > 0 && (this.connectionTimeoutHandle = setTimeout(() => {
        n._ending = true, n.stream.destroy(new Error("timeout expired"));
      }, this._connectionTimeoutMillis)), this.host && this.host.indexOf("/") === 0 ? n.connect(this.host + "/.s.PGSQL." + this.port) : n.connect(this.port, this.host), n.on("connect", function() {
        t.ssl ? n.requestSsl() : n.startup(t.getStartupConf());
      }), n.on("sslconnect", function() {
        n.startup(t.getStartupConf());
      }), this._attachListeners(
        n
      ), n.once("end", () => {
        let i = this._ending ? new Error("Connection terminated") : new Error("Connection terminated unexpectedly");
        clearTimeout(this.connectionTimeoutHandle), this._errorAllQueries(i), this._ending || (this._connecting && !this._connectionError ? this._connectionCallback ? this._connectionCallback(i) : this._handleErrorEvent(i) : this._connectionError || this._handleErrorEvent(i)), y.nextTick(() => {
          this.emit("end");
        });
      });
    }
    connect(e) {
      if (e) {
        this._connect(e);
        return;
      }
      return new this._Promise((t, n) => {
        this._connect((i) => {
          i ? n(i) : t();
        });
      });
    }
    _attachListeners(e) {
      e.on("authenticationCleartextPassword", this._handleAuthCleartextPassword.bind(this)), e.on("authenticationMD5Password", this._handleAuthMD5Password.bind(this)), e.on("authenticationSASL", this._handleAuthSASL.bind(this)), e.on("authenticationSASLContinue", this._handleAuthSASLContinue.bind(this)), e.on("authenticationSASLFinal", this._handleAuthSASLFinal.bind(this)), e.on("backendKeyData", this._handleBackendKeyData.bind(this)), e.on("error", this._handleErrorEvent.bind(this)), e.on("errorMessage", this._handleErrorMessage.bind(this)), e.on("readyForQuery", this._handleReadyForQuery.bind(this)), e.on("notice", this._handleNotice.bind(this)), e.on("rowDescription", this._handleRowDescription.bind(this)), e.on("dataRow", this._handleDataRow.bind(this)), e.on("portalSuspended", this._handlePortalSuspended.bind(
        this
      )), e.on("emptyQuery", this._handleEmptyQuery.bind(this)), e.on("commandComplete", this._handleCommandComplete.bind(this)), e.on("parseComplete", this._handleParseComplete.bind(this)), e.on("copyInResponse", this._handleCopyInResponse.bind(this)), e.on("copyData", this._handleCopyData.bind(this)), e.on("notification", this._handleNotification.bind(this));
    }
    _checkPgPass(e) {
      let t = this.connection;
      typeof this.password == "function" ? this._Promise.resolve().then(() => this.password()).then((n) => {
        if (n !== void 0) {
          if (typeof n != "string") {
            t.emit("error", new TypeError(
              "Password must be a string"
            ));
            return;
          }
          this.connectionParameters.password = this.password = n;
        } else this.connectionParameters.password = this.password = null;
        e();
      }).catch((n) => {
        t.emit("error", n);
      }) : this.password !== null ? e() : xl(
        this.connectionParameters,
        (n) => {
          n !== void 0 && (this.connectionParameters.password = this.password = n), e();
        }
      );
    }
    _handleAuthCleartextPassword(e) {
      this._checkPgPass(() => {
        this.connection.password(this.password);
      });
    }
    _handleAuthMD5Password(e) {
      this._checkPgPass(
        () => {
          let t = bl.postgresMd5PasswordHash(this.user, this.password, e.salt);
          this.connection.password(t);
        }
      );
    }
    _handleAuthSASL(e) {
      this._checkPgPass(() => {
        this.saslSession = Cn.startSession(e.mechanisms), this.connection.sendSASLInitialResponseMessage(
          this.saslSession.mechanism,
          this.saslSession.response
        );
      });
    }
    _handleAuthSASLContinue(e) {
      Cn.continueSession(
        this.saslSession,
        this.password,
        e.data
      ), this.connection.sendSCRAMClientFinalMessage(this.saslSession.response);
    }
    _handleAuthSASLFinal(e) {
      Cn.finalizeSession(this.saslSession, e.data), this.saslSession = null;
    }
    _handleBackendKeyData(e) {
      this.processID = e.processID, this.secretKey = e.secretKey;
    }
    _handleReadyForQuery(e) {
      this._connecting && (this._connecting = false, this._connected = true, clearTimeout(this.connectionTimeoutHandle), this._connectionCallback && (this._connectionCallback(null, this), this._connectionCallback = null), this.emit("connect"));
      let { activeQuery: t } = this;
      this.activeQuery = null, this.readyForQuery = true, t && t.handleReadyForQuery(this.connection), this._pulseQueryQueue();
    }
    _handleErrorWhileConnecting(e) {
      if (!this._connectionError) {
        if (this._connectionError = true, clearTimeout(this.connectionTimeoutHandle), this._connectionCallback) return this._connectionCallback(e);
        this.emit("error", e);
      }
    }
    _handleErrorEvent(e) {
      if (this._connecting) return this._handleErrorWhileConnecting(e);
      this._queryable = false, this._errorAllQueries(e), this.emit("error", e);
    }
    _handleErrorMessage(e) {
      if (this._connecting) return this._handleErrorWhileConnecting(e);
      let t = this.activeQuery;
      if (!t) {
        this._handleErrorEvent(e);
        return;
      }
      this.activeQuery = null, t.handleError(
        e,
        this.connection
      );
    }
    _handleRowDescription(e) {
      this.activeQuery.handleRowDescription(e);
    }
    _handleDataRow(e) {
      this.activeQuery.handleDataRow(e);
    }
    _handlePortalSuspended(e) {
      this.activeQuery.handlePortalSuspended(this.connection);
    }
    _handleEmptyQuery(e) {
      this.activeQuery.handleEmptyQuery(this.connection);
    }
    _handleCommandComplete(e) {
      this.activeQuery.handleCommandComplete(e, this.connection);
    }
    _handleParseComplete(e) {
      this.activeQuery.name && (this.connection.parsedStatements[this.activeQuery.name] = this.activeQuery.text);
    }
    _handleCopyInResponse(e) {
      this.activeQuery.handleCopyInResponse(this.connection);
    }
    _handleCopyData(e) {
      this.activeQuery.handleCopyData(
        e,
        this.connection
      );
    }
    _handleNotification(e) {
      this.emit("notification", e);
    }
    _handleNotice(e) {
      this.emit("notice", e);
    }
    getStartupConf() {
      var e = this.connectionParameters, t = { user: e.user, database: e.database }, n = e.application_name || e.fallback_application_name;
      return n && (t.application_name = n), e.replication && (t.replication = "" + e.replication), e.statement_timeout && (t.statement_timeout = String(parseInt(e.statement_timeout, 10))), e.lock_timeout && (t.lock_timeout = String(parseInt(e.lock_timeout, 10))), e.idle_in_transaction_session_timeout && (t.idle_in_transaction_session_timeout = String(parseInt(e.idle_in_transaction_session_timeout, 10))), e.options && (t.options = e.options), t;
    }
    cancel(e, t) {
      if (e.activeQuery === t) {
        var n = this.connection;
        this.host && this.host.indexOf("/") === 0 ? n.connect(this.host + "/.s.PGSQL." + this.port) : n.connect(this.port, this.host), n.on("connect", function() {
          n.cancel(
            e.processID,
            e.secretKey
          );
        });
      } else e.queryQueue.indexOf(t) !== -1 && e.queryQueue.splice(e.queryQueue.indexOf(t), 1);
    }
    setTypeParser(e, t, n) {
      return this._types.setTypeParser(e, t, n);
    }
    getTypeParser(e, t) {
      return this._types.getTypeParser(e, t);
    }
    escapeIdentifier(e) {
      return '"' + e.replace(/"/g, '""') + '"';
    }
    escapeLiteral(e) {
      for (var t = false, n = "'", i = 0; i < e.length; i++) {
        var s = e[i];
        s === "'" ? n += s + s : s === "\\" ? (n += s + s, t = true) : n += s;
      }
      return n += "'", t === true && (n = " E" + n), n;
    }
    _pulseQueryQueue() {
      if (this.readyForQuery === true) if (this.activeQuery = this.queryQueue.shift(), this.activeQuery) {
        this.readyForQuery = false, this.hasExecuted = true;
        let e = this.activeQuery.submit(this.connection);
        e && y.nextTick(() => {
          this.activeQuery.handleError(e, this.connection), this.readyForQuery = true, this._pulseQueryQueue();
        });
      } else this.hasExecuted && (this.activeQuery = null, this.emit("drain"));
    }
    query(e, t, n) {
      var i, s, o, u, c;
      if (e == null) throw new TypeError(
        "Client was passed a null or undefined query"
      );
      return typeof e.submit == "function" ? (o = e.query_timeout || this.connectionParameters.query_timeout, s = i = e, typeof t == "function" && (i.callback = i.callback || t)) : (o = this.connectionParameters.query_timeout, i = new oo(e, t, n), i.callback || (s = new this._Promise((l, f) => {
        i.callback = (m, g) => m ? f(m) : l(g);
      }))), o && (c = i.callback, u = setTimeout(() => {
        var l = new Error("Query read timeout");
        y.nextTick(
          () => {
            i.handleError(l, this.connection);
          }
        ), c(l), i.callback = () => {
        };
        var f = this.queryQueue.indexOf(i);
        f > -1 && this.queryQueue.splice(f, 1), this._pulseQueryQueue();
      }, o), i.callback = (l, f) => {
        clearTimeout(u), c(l, f);
      }), this.binary && !i.binary && (i.binary = true), i._result && !i._result._types && (i._result._types = this._types), this._queryable ? this._ending ? (y.nextTick(() => {
        i.handleError(new Error("Client was closed and is not queryable"), this.connection);
      }), s) : (this.queryQueue.push(i), this._pulseQueryQueue(), s) : (y.nextTick(() => {
        i.handleError(new Error("Client has encountered a connection error and is not queryable"), this.connection);
      }), s);
    }
    ref() {
      this.connection.ref();
    }
    unref() {
      this.connection.unref();
    }
    end(e) {
      if (this._ending = true, !this.connection._connecting) if (e) e();
      else return this._Promise.resolve();
      if (this.activeQuery || !this._queryable ? this.connection.stream.destroy() : this.connection.end(), e) this.connection.once("end", e);
      else return new this._Promise((t) => {
        this.connection.once("end", t);
      });
    }
  };
  a(_n, "Client");
  var Ut = _n;
  Ut.Query = oo;
  ao.exports = Ut;
});
var fo = T((Gd, lo) => {
  "use strict";
  h();
  var Cl = ve().EventEmitter, Tn = a(function() {
  }, "NOOP"), co = a((r, e) => {
    let t = r.findIndex(e);
    return t === -1 ? void 0 : r.splice(t, 1)[0];
  }, "removeWhere"), Rn = class Rn {
    static {
      __name(this, "Rn");
    }
    constructor(e, t, n) {
      this.client = e, this.idleListener = t, this.timeoutId = n;
    }
  };
  a(Rn, "IdleItem");
  var In = Rn, Ln = class Ln {
    static {
      __name(this, "Ln");
    }
    constructor(e) {
      this.callback = e;
    }
  };
  a(Ln, "PendingItem");
  var qe = Ln;
  function _l() {
    throw new Error("Release called on client which has already been released to the pool.");
  }
  __name(_l, "_l");
  a(_l, "throwOnDoubleRelease");
  function Qt(r, e) {
    if (e)
      return { callback: e, result: void 0 };
    let t, n, i = a(function(o, u) {
      o ? t(o) : n(u);
    }, "cb"), s = new r(function(o, u) {
      n = o, t = u;
    }).catch((o) => {
      throw Error.captureStackTrace(o), o;
    });
    return { callback: i, result: s };
  }
  __name(Qt, "Qt");
  a(Qt, "promisify");
  function Tl(r, e) {
    return a(/* @__PURE__ */ __name(function t(n) {
      n.client = e, e.removeListener("error", t), e.on("error", () => {
        r.log(
          "additional client error after disconnection due to error",
          n
        );
      }), r._remove(e), r.emit("error", n, e);
    }, "t"), "idleListener");
  }
  __name(Tl, "Tl");
  a(Tl, "makeIdleListener");
  var Bn = class Bn extends Cl {
    static {
      __name(this, "Bn");
    }
    constructor(e, t) {
      super(), this.options = Object.assign({}, e), e != null && "password" in e && Object.defineProperty(this.options, "password", {
        configurable: true,
        enumerable: false,
        writable: true,
        value: e.password
      }), e != null && e.ssl && e.ssl.key && Object.defineProperty(this.options.ssl, "key", { enumerable: false }), this.options.max = this.options.max || this.options.poolSize || 10, this.options.min = this.options.min || 0, this.options.maxUses = this.options.maxUses || 1 / 0, this.options.allowExitOnIdle = this.options.allowExitOnIdle || false, this.options.maxLifetimeSeconds = this.options.maxLifetimeSeconds || 0, this.log = this.options.log || function() {
      }, this.Client = this.options.Client || t || ot().Client, this.Promise = this.options.Promise || b.Promise, typeof this.options.idleTimeoutMillis > "u" && (this.options.idleTimeoutMillis = 1e4), this._clients = [], this._idle = [], this._expired = /* @__PURE__ */ new WeakSet(), this._pendingQueue = [], this._endCallback = void 0, this.ending = false, this.ended = false;
    }
    _promiseTry(e) {
      let t = this.Promise;
      return typeof t.try == "function" ? t.try(e) : new t((n) => n(e()));
    }
    _isFull() {
      return this._clients.length >= this.options.max;
    }
    _isAboveMin() {
      return this._clients.length > this.options.min;
    }
    _pulseQueue() {
      if (this.log("pulse queue"), this.ended) {
        this.log("pulse queue ended");
        return;
      }
      if (this.ending) {
        this.log("pulse queue on ending"), this._idle.length && this._idle.slice().map((t) => {
          this._remove(t.client);
        }), this._clients.length || (this.ended = true, this._endCallback());
        return;
      }
      if (!this._pendingQueue.length) {
        this.log("no queued requests");
        return;
      }
      if (!this._idle.length && this._isFull())
        return;
      let e = this._pendingQueue.shift();
      if (this._idle.length) {
        let t = this._idle.pop();
        clearTimeout(t.timeoutId);
        let n = t.client;
        n.ref && n.ref();
        let i = t.idleListener;
        return this._acquireClient(n, e, i, false);
      }
      if (!this._isFull()) return this.newClient(e);
      throw new Error("unexpected condition");
    }
    _remove(e, t) {
      let n = co(this._idle, (s) => s.client === e);
      n !== void 0 && clearTimeout(n.timeoutId), this._clients = this._clients.filter((s) => s !== e);
      let i = this;
      e.end(() => {
        i.emit("remove", e), typeof t == "function" && t();
      });
    }
    connect(e) {
      if (this.ending) {
        let i = new Error(
          "Cannot use a pool after calling end on the pool"
        );
        return e ? e(i) : this.Promise.reject(i);
      }
      let t = Qt(this.Promise, e), n = t.result;
      if (this._isFull() || this._idle.length) {
        if (this._idle.length && y.nextTick(() => this._pulseQueue()), !this.options.connectionTimeoutMillis) return this._pendingQueue.push(new qe(t.callback)), n;
        let i = a((u, c, l) => {
          clearTimeout(o), t.callback(u, c, l);
        }, "queueCallback"), s = new qe(i), o = setTimeout(() => {
          co(this._pendingQueue, (u) => u.callback === i), s.timedOut = true, t.callback(new Error("timeout exceeded when trying to connect"));
        }, this.options.connectionTimeoutMillis);
        return o.unref && o.unref(), this._pendingQueue.push(s), n;
      }
      return this.newClient(new qe(t.callback)), n;
    }
    newClient(e) {
      let t = new this.Client(this.options);
      this._clients.push(t);
      let n = Tl(this, t);
      this.log("checking client timeout");
      let i, s = false;
      this.options.connectionTimeoutMillis && (i = setTimeout(() => {
        t.connection ? (this.log("ending client due to timeout"), s = true, t.connection.stream.destroy()) : t.isConnected() || (this.log("ending client due to timeout"), s = true, t.end());
      }, this.options.connectionTimeoutMillis)), this.log("connecting new client"), t.connect((o) => {
        if (i && clearTimeout(i), t.on("error", n), o) this.log("client failed to connect", o), this._clients = this._clients.filter((u) => u !== t), s && (o = new Error("Connection terminated due to connection timeout", { cause: o })), this._pulseQueue(), e.timedOut || e.callback(
          o,
          void 0,
          Tn
        );
        else {
          if (this.log("new client connected"), this.options.onConnect) {
            this._promiseTry(() => this.options.onConnect(t)).then(() => {
              this._afterConnect(t, e, n);
            }, (u) => {
              this._clients = this._clients.filter((c) => c !== t), t.end(() => {
                this._pulseQueue(), e.timedOut || e.callback(u, void 0, Tn);
              });
            });
            return;
          }
          return this._afterConnect(
            t,
            e,
            n
          );
        }
      });
    }
    _afterConnect(e, t, n) {
      if (this.options.maxLifetimeSeconds !== 0) {
        let i = setTimeout(() => {
          this.log(
            "ending client due to expired lifetime"
          ), this._expired.add(e), this._idle.findIndex((o) => o.client === e) !== -1 && this._acquireClient(e, new qe((o, u, c) => c()), n, false);
        }, this.options.maxLifetimeSeconds * 1e3);
        i.unref(), e.once("end", () => clearTimeout(i));
      }
      return this._acquireClient(e, t, n, true);
    }
    _acquireClient(e, t, n, i) {
      i && this.emit("connect", e), this.emit("acquire", e), e.release = this._releaseOnce(e, n), e.removeListener("error", n), t.timedOut ? i && this.options.verify ? this.options.verify(e, e.release) : e.release() : i && this.options.verify ? this.options.verify(e, (s) => {
        if (s) return e.release(s), t.callback(s, void 0, Tn);
        t.callback(void 0, e, e.release);
      }) : t.callback(void 0, e, e.release);
    }
    _releaseOnce(e, t) {
      let n = false;
      return (i) => {
        n && _l(), n = true, this._release(
          e,
          t,
          i
        );
      };
    }
    _release(e, t, n) {
      if (e.on("error", t), e._poolUseCount = (e._poolUseCount || 0) + 1, this.emit(
        "release",
        n,
        e
      ), n || this.ending || !e._queryable || e._ending || e._poolUseCount >= this.options.maxUses) return e._poolUseCount >= this.options.maxUses && this.log("remove expended client"), this._remove(e, this._pulseQueue.bind(this));
      if (this._expired.has(e)) return this.log("remove expired client"), this._expired.delete(e), this._remove(
        e,
        this._pulseQueue.bind(this)
      );
      let s;
      this.options.idleTimeoutMillis && this._isAboveMin() && (s = setTimeout(
        () => {
          this._isAboveMin() && (this.log("remove idle client"), this._remove(e, this._pulseQueue.bind(this)));
        },
        this.options.idleTimeoutMillis
      ), this.options.allowExitOnIdle && s.unref()), this.options.allowExitOnIdle && e.unref(), this._idle.push(new In(e, t, s)), this._pulseQueue();
    }
    query(e, t, n) {
      if (typeof e == "function") {
        let s = Qt(
          this.Promise,
          e
        );
        return x(function() {
          return s.callback(new Error("Passing a function as the first parameter to pool.query is not supported"));
        }), s.result;
      }
      typeof t == "function" && (n = t, t = void 0);
      let i = Qt(this.Promise, n);
      return n = i.callback, this.connect((s, o) => {
        if (s) return n(s);
        let u = false, c = a((l) => {
          u || (u = true, o.release(
            l
          ), n(l));
        }, "onError");
        o.once("error", c), this.log("dispatching query");
        try {
          o.query(e, t, (l, f) => {
            if (this.log("query dispatched"), o.removeListener("error", c), !u) return u = true, o.release(l), l ? n(l) : n(void 0, f);
          });
        } catch (l) {
          return o.release(l), n(l);
        }
      }), i.result;
    }
    end(e) {
      if (this.log("ending"), this.ending) {
        let n = new Error("Called end on pool more than once");
        return e ? e(n) : this.Promise.reject(n);
      }
      this.ending = true;
      let t = Qt(
        this.Promise,
        e
      );
      return this._endCallback = t.callback, this._pulseQueue(), t.result;
    }
    get waitingCount() {
      return this._pendingQueue.length;
    }
    get idleCount() {
      return this._idle.length;
    }
    get expiredCount() {
      return this._clients.reduce((e, t) => e + (this._expired.has(t) ? 1 : 0), 0);
    }
    get totalCount() {
      return this._clients.length;
    }
  };
  a(Bn, "Pool");
  var Pn = Bn;
  lo.exports = Pn;
});
var ho = {};
se(ho, { default: /* @__PURE__ */ __name(() => Il, "default") });
var Il;
var po = V(() => {
  "use strict";
  h();
  Il = {};
});
var yo = T((Yd, Pl) => {
  Pl.exports = { name: "pg", version: "8.8.0", description: "PostgreSQL client - pure javascript & libpq with the same API", keywords: [
    "database",
    "libpq",
    "pg",
    "postgre",
    "postgres",
    "postgresql",
    "rdbms"
  ], homepage: "https://github.com/brianc/node-postgres", repository: { type: "git", url: "git://github.com/brianc/node-postgres.git", directory: "packages/pg" }, author: "Brian Carlson <brian.m.carlson@gmail.com>", main: "./lib", dependencies: { "buffer-writer": "2.0.0", "packet-reader": "1.0.0", "pg-connection-string": "^2.5.0", "pg-pool": "^3.5.2", "pg-protocol": "^1.5.0", "pg-types": "^2.1.0", pgpass: "1.x" }, devDependencies: {
    async: "2.6.4",
    bluebird: "3.5.2",
    co: "4.6.0",
    "pg-copy-streams": "0.3.0"
  }, peerDependencies: { "pg-native": ">=3.0.1" }, peerDependenciesMeta: { "pg-native": { optional: true } }, scripts: { test: "make test-all" }, files: ["lib", "SPONSORS.md"], license: "MIT", engines: { node: ">= 8.0.0" }, gitHead: "c99fb2c127ddf8d712500db2c7b9a5491a178655" };
});
var wo = T((Zd, go) => {
  "use strict";
  h();
  var mo = ve().EventEmitter, Rl = (it(), O(nt)), Fn = rt(), Ne = go.exports = function(r, e, t) {
    mo.call(this), r = Fn.normalizeQueryConfig(r, e, t), this.text = r.text, this.values = r.values, this.name = r.name, this.callback = r.callback, this.state = "new", this._arrayMode = r.rowMode === "array", this._emitRowEvents = false, this.on("newListener", function(n) {
      n === "row" && (this._emitRowEvents = true);
    }.bind(this));
  };
  Rl.inherits(Ne, mo);
  var Ll = { sqlState: "code", statementPosition: "position", messagePrimary: "message", context: "where", schemaName: "schema", tableName: "table", columnName: "column", dataTypeName: "dataType", constraintName: "constraint", sourceFile: "file", sourceLine: "line", sourceFunction: "routine" };
  Ne.prototype.handleError = function(r) {
    var e = this.native.pq.resultErrorFields();
    if (e) for (var t in e) {
      var n = Ll[t] || t;
      r[n] = e[t];
    }
    this.callback ? this.callback(r) : this.emit("error", r), this.state = "error";
  };
  Ne.prototype.then = function(r, e) {
    return this._getPromise().then(
      r,
      e
    );
  };
  Ne.prototype.catch = function(r) {
    return this._getPromise().catch(r);
  };
  Ne.prototype._getPromise = function() {
    return this._promise ? this._promise : (this._promise = new Promise(function(r, e) {
      this._once("end", r), this._once("error", e);
    }.bind(this)), this._promise);
  };
  Ne.prototype.submit = function(r) {
    this.state = "running";
    var e = this;
    this.native = r.native, r.native.arrayMode = this._arrayMode;
    var t = a(function(s, o, u) {
      if (r.native.arrayMode = false, x(function() {
        e.emit("_done");
      }), s) return e.handleError(s);
      e._emitRowEvents && (u.length > 1 ? o.forEach(
        (c, l) => {
          c.forEach((f) => {
            e.emit("row", f, u[l]);
          });
        }
      ) : o.forEach(function(c) {
        e.emit("row", c, u);
      })), e.state = "end", e.emit("end", u), e.callback && e.callback(null, u);
    }, "after");
    if (y.domain && (t = y.domain.bind(t)), this.name) {
      this.name.length > 63 && (console.error("Warning! Postgres only supports 63 characters for query names."), console.error("You supplied %s (%s)", this.name, this.name.length), console.error("This can cause conflicts and silent errors executing queries"));
      var n = (this.values || []).map(Fn.prepareValue);
      if (r.namedQueries[this.name]) {
        if (this.text && r.namedQueries[this.name] !== this.text) {
          let s = new Error(`Prepared statements must be unique - '${this.name}' was used for a different statement`);
          return t(s);
        }
        return r.native.execute(this.name, n, t);
      }
      return r.native.prepare(this.name, this.text, n.length, function(s) {
        return s ? t(s) : (r.namedQueries[e.name] = e.text, e.native.execute(e.name, n, t));
      });
    } else if (this.values) {
      if (!Array.isArray(
        this.values
      )) {
        let s = new Error("Query values must be an array");
        return t(s);
      }
      var i = this.values.map(Fn.prepareValue);
      r.native.query(this.text, i, t);
    } else r.native.query(this.text, t);
  };
});
var So = T((tp, vo) => {
  "use strict";
  h();
  var Bl = (po(), O(ho)), Fl = _t(), ep = yo(), bo = ve().EventEmitter, Ml = (it(), O(nt)), kl = Lt(), xo = wo(), Y = vo.exports = function(r) {
    bo.call(this), r = r || {}, this._Promise = r.Promise || b.Promise, this._types = new Fl(r.types), this.native = new Bl({ types: this._types }), this._queryQueue = [], this._ending = false, this._connecting = false, this._connected = false, this._queryable = true;
    var e = this.connectionParameters = new kl(r);
    this.user = e.user, Object.defineProperty(this, "password", { configurable: true, enumerable: false, writable: true, value: e.password }), this.database = e.database, this.host = e.host, this.port = e.port, this.namedQueries = {};
  };
  Y.Query = xo;
  Ml.inherits(Y, bo);
  Y.prototype._errorAllQueries = function(r) {
    let e = a((t) => {
      y.nextTick(() => {
        t.native = this.native, t.handleError(r);
      });
    }, "enqueueError");
    this._hasActiveQuery() && (e(this._activeQuery), this._activeQuery = null), this._queryQueue.forEach(e), this._queryQueue.length = 0;
  };
  Y.prototype._connect = function(r) {
    var e = this;
    if (this._connecting) {
      y.nextTick(() => r(new Error("Client has already been connected. You cannot reuse a client.")));
      return;
    }
    this._connecting = true, this.connectionParameters.getLibpqConnectionString(function(t, n) {
      if (t) return r(t);
      e.native.connect(n, function(i) {
        if (i) return e.native.end(), r(i);
        e._connected = true, e.native.on("error", function(s) {
          e._queryable = false, e._errorAllQueries(s), e.emit("error", s);
        }), e.native.on("notification", function(s) {
          e.emit("notification", { channel: s.relname, payload: s.extra });
        }), e.emit("connect"), e._pulseQueryQueue(true), r();
      });
    });
  };
  Y.prototype.connect = function(r) {
    if (r) {
      this._connect(r);
      return;
    }
    return new this._Promise((e, t) => {
      this._connect((n) => {
        n ? t(n) : e();
      });
    });
  };
  Y.prototype.query = function(r, e, t) {
    var n, i, s, o, u;
    if (r == null) throw new TypeError("Client was passed a null or undefined query");
    if (typeof r.submit == "function") s = r.query_timeout || this.connectionParameters.query_timeout, i = n = r, typeof e == "function" && (r.callback = e);
    else if (s = this.connectionParameters.query_timeout, n = new xo(r, e, t), !n.callback) {
      let c, l;
      i = new this._Promise((f, m) => {
        c = f, l = m;
      }), n.callback = (f, m) => f ? l(f) : c(m);
    }
    return s && (u = n.callback, o = setTimeout(() => {
      var c = new Error(
        "Query read timeout"
      );
      y.nextTick(() => {
        n.handleError(c, this.connection);
      }), u(c), n.callback = () => {
      };
      var l = this._queryQueue.indexOf(n);
      l > -1 && this._queryQueue.splice(l, 1), this._pulseQueryQueue();
    }, s), n.callback = (c, l) => {
      clearTimeout(o), u(c, l);
    }), this._queryable ? this._ending ? (n.native = this.native, y.nextTick(() => {
      n.handleError(
        new Error("Client was closed and is not queryable")
      );
    }), i) : (this._queryQueue.push(n), this._pulseQueryQueue(), i) : (n.native = this.native, y.nextTick(() => {
      n.handleError(new Error("Client has encountered a connection error and is not queryable"));
    }), i);
  };
  Y.prototype.end = function(r) {
    var e = this;
    this._ending = true, this._connected || this.once("connect", this.end.bind(this, r));
    var t;
    return r || (t = new this._Promise(function(n, i) {
      r = a((s) => s ? i(s) : n(), "cb");
    })), this.native.end(function() {
      e._errorAllQueries(new Error("Connection terminated")), y.nextTick(() => {
        e.emit("end"), r && r();
      });
    }), t;
  };
  Y.prototype._hasActiveQuery = function() {
    return this._activeQuery && this._activeQuery.state !== "error" && this._activeQuery.state !== "end";
  };
  Y.prototype._pulseQueryQueue = function(r) {
    if (this._connected && !this._hasActiveQuery()) {
      var e = this._queryQueue.shift();
      if (!e) {
        r || this.emit("drain");
        return;
      }
      this._activeQuery = e, e.submit(this);
      var t = this;
      e.once("_done", function() {
        t._pulseQueryQueue();
      });
    }
  };
  Y.prototype.cancel = function(r) {
    this._activeQuery === r ? this.native.cancel(function() {
    }) : this._queryQueue.indexOf(r) !== -1 && this._queryQueue.splice(this._queryQueue.indexOf(r), 1);
  };
  Y.prototype.ref = function() {
  };
  Y.prototype.unref = function() {
  };
  Y.prototype.setTypeParser = function(r, e, t) {
    return this._types.setTypeParser(
      r,
      e,
      t
    );
  };
  Y.prototype.getTypeParser = function(r, e) {
    return this._types.getTypeParser(r, e);
  };
});
var Mn = T((ip, Eo) => {
  "use strict";
  h();
  Eo.exports = So();
});
var ot = T((op, at) => {
  "use strict";
  h();
  var Ol = uo(), Ul = tt(), Ql = An(), Dl = fo(), { DatabaseError: ql } = vn(), Nl = a(
    (r) => {
      var e;
      return e = class extends Dl {
        static {
          __name(this, "e");
        }
        constructor(n) {
          super(n, r);
        }
      }, a(e, "BoundPool"), e;
    },
    "poolFactory"
  ), kn = a(
    function(r) {
      this.defaults = Ul, this.Client = r, this.Query = this.Client.Query, this.Pool = Nl(this.Client), this._pools = [], this.Connection = Ql, this.types = Je(), this.DatabaseError = ql;
    },
    "PG"
  );
  typeof y.env.NODE_PG_FORCE_NATIVE < "u" ? at.exports = new kn(Mn()) : (at.exports = new kn(Ol), Object.defineProperty(at.exports, "native", {
    configurable: true,
    enumerable: false,
    get() {
      var r = null;
      try {
        r = new kn(Mn());
      } catch (e) {
        if (e.code !== "MODULE_NOT_FOUND") throw e;
      }
      return Object.defineProperty(at.exports, "native", { value: r }), r;
    }
  }));
});
h();
h();
h();
var da = Object.defineProperty;
var pa = Object.defineProperties;
var ya = Object.getOwnPropertyDescriptors;
var ai = Object.getOwnPropertySymbols;
var ma = Object.prototype.hasOwnProperty;
var ga = Object.prototype.propertyIsEnumerable;
var ui = a(
  (r, e, t) => e in r ? da(r, e, { enumerable: true, configurable: true, writable: true, value: t }) : r[e] = t,
  "__defNormalProp"
);
var wa = a((r, e) => {
  for (var t in e || (e = {})) ma.call(e, t) && ui(r, t, e[t]);
  if (ai) for (var t of ai(e)) ga.call(e, t) && ui(r, t, e[t]);
  return r;
}, "__spreadValues");
var ba = a((r, e) => pa(r, ya(e)), "__spreadProps");
var xa = 1008e3;
var ci = new Uint8Array(
  new Uint16Array([258]).buffer
)[0] === 2;
var va = new TextDecoder();
var Yt = new TextEncoder();
var dt = Yt.encode("0123456789abcdef");
var pt = Yt.encode("0123456789ABCDEF");
var Sa = Yt.encode("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/");
var li = Sa.slice();
li[62] = 45;
li[63] = 95;
var je;
var yt;
function Ea(r, { alphabet: e, scratchArr: t } = {}) {
  if (!je) if (je = new Uint16Array(256), yt = new Uint16Array(256), ci) for (let S = 0; S < 256; S++) je[S] = dt[S & 15] << 8 | dt[S >>> 4], yt[S] = pt[S & 15] << 8 | pt[S >>> 4];
  else for (let S = 0; S < 256; S++) je[S] = dt[S & 15] | dt[S >>> 4] << 8, yt[S] = pt[S & 15] | pt[S >>> 4] << 8;
  r.byteOffset % 4 !== 0 && (r = new Uint8Array(r));
  let n = r.length, i = n >>> 1, s = n >>> 2, o = t || new Uint16Array(n), u = new Uint32Array(
    r.buffer,
    r.byteOffset,
    s
  ), c = new Uint32Array(o.buffer, o.byteOffset, i), l = e === "upper" ? yt : je, f = 0, m = 0, g;
  if (ci)
    for (; f < s; ) g = u[f++], c[m++] = l[g >>> 8 & 255] << 16 | l[g & 255], c[m++] = l[g >>> 24] << 16 | l[g >>> 16 & 255];
  else for (; f < s; )
    g = u[f++], c[m++] = l[g >>> 24] << 16 | l[g >>> 16 & 255], c[m++] = l[g >>> 8 & 255] << 16 | l[g & 255];
  for (f <<= 2; f < n; ) o[f] = l[r[f++]];
  return va.decode(o.subarray(0, n));
}
__name(Ea, "Ea");
a(Ea, "_toHex");
function Aa(r, e = {}) {
  let t = "", n = r.length, i = xa >>> 1, s = Math.ceil(n / i), o = new Uint16Array(s > 1 ? i : n), u = ba(wa({}, e), { scratchArr: o });
  for (let c = 0; c < s; c++) {
    let l = c * i, f = l + i;
    t += Ea(r.subarray(l, f), u);
  }
  return t;
}
__name(Aa, "Aa");
a(Aa, "_toHexChunked");
function fi(r, e = {}) {
  return e.alphabet !== "upper" && typeof r.toHex == "function" ? r.toHex() : Aa(r, e);
}
__name(fi, "fi");
a(fi, "toHex");
h();
h();
var Zt = class Zt2 {
  static {
    __name(this, "Zt");
  }
  constructor(e, t, n) {
    E(this, "execute", e);
    E(this, "queryData", t);
    E(this, "opts", n);
  }
  then(e, t) {
    return this.execute(this.queryData, this.opts).then(e, t);
  }
  catch(e) {
    return this.execute(
      this.queryData,
      this.opts
    ).catch(e);
  }
  finally(e) {
    return this.execute(this.queryData, this.opts).finally(e);
  }
};
a(Zt, "NeonQueryPromise");
var xe = Zt;
var mt = class mt2 {
  static {
    __name(this, "mt");
  }
  constructor(e, t) {
    E(this, "strings", e);
    E(this, "values", t);
  }
  toParameterizedQuery(e = {
    query: "",
    params: []
  }) {
    let { strings: t, values: n } = this;
    for (let i = 0, s = t.length; i < s; i++) if (e.query += t[i], i < n.length) {
      let o = n[i];
      if (o instanceof $e) e.query += o.sql;
      else if (o instanceof xe) if (o.queryData instanceof mt2) o.queryData.toParameterizedQuery(e);
      else {
        if (o.queryData.params?.length) throw new Error("This query is not composable");
        e.query += o.queryData.query;
      }
      else {
        let { params: u } = e;
        u.push(o), e.query += "$" + u.length, (o instanceof p || ArrayBuffer.isView(o)) && (e.query += "::bytea");
      }
    }
    return e;
  }
};
a(mt, "SqlTemplate");
var He = mt;
var Jt = class Jt2 {
  static {
    __name(this, "Jt");
  }
  constructor(e) {
    E(this, "sql", e);
  }
};
a(Jt, "UnsafeRawSql");
var $e = Jt;
h();
function gt() {
  typeof window < "u" && typeof document < "u" && typeof console < "u" && typeof console.warn == "function" && console.warn(`          
        ************************************************************
        *                                                          *
        *  WARNING: Running SQL directly from the browser can have *
        *  security implications. Even if your database is         *
        *  protected by Row-Level Security (RLS), use it at your   *
        *  own risk. This approach is great for fast prototyping,  *
        *  but ensure proper safeguards are in place to prevent    *
        *  misuse or execution of expensive SQL queries by your    *
        *  end users.                                              *
        *                                                          *
        *  If you've assessed the risks, suppress this message     *
        *  using the disableWarningInBrowsers configuration        *
        *  parameter.                                              *
        *                                                          *
        ************************************************************`);
}
__name(gt, "gt");
a(gt, "warnIfBrowser");
h();
h();
var wt = class wt2 extends Error {
  static {
    __name(this, "wt");
  }
  constructor(t) {
    super(t);
    E(this, "name", "NeonDbError");
    E(this, "severity");
    E(this, "code");
    E(this, "detail");
    E(this, "hint");
    E(this, "position");
    E(this, "internalPosition");
    E(
      this,
      "internalQuery"
    );
    E(this, "where");
    E(this, "schema");
    E(this, "table");
    E(this, "column");
    E(this, "dataType");
    E(this, "constraint");
    E(this, "file");
    E(this, "line");
    E(this, "routine");
    E(this, "sourceError");
    "captureStackTrace" in Error && typeof Error.captureStackTrace == "function" && Error.captureStackTrace(this, wt2);
  }
};
a(
  wt,
  "NeonDbError"
);
var N = wt;
var hi = ["severity", "code", "detail", "hint", "position", "internalPosition", "internalQuery", "where", "schema", "table", "column", "dataType", "constraint", "file", "line", "routine"];
function di(r, e) {
  let t, n;
  try {
    t = new URL(r).protocol, n = new URL("http:" + r.slice(t.length));
  } catch {
    throw new N(
      `Database connection string provided to neon() is not a valid URL (connection string: ${r})`
    );
  }
  let {
    username: i,
    hostname: s,
    pathname: o
  } = n;
  if (t !== "postgres:" && t !== "postgresql:" || e && (!i || !s || s === "-" || !o || o === "/")) throw new N(
    "Wrong URL scheme or missing user, host or database in connection parameters"
  );
  return n;
}
__name(di, "di");
a(di, "URLFromPgConnectionString");
function Ca(r) {
  return "postgresql:" + r.href.slice(r.protocol.length);
}
__name(Ca, "Ca");
a(Ca, "pgConnectionStringFromURL");
var _a = ["connectionString", "user", "username", "password", "host", "hostname", "port", "database"];
var Ta = { database: "pathname", user: "username", host: "hostname" };
function pi(...r) {
  let e = {};
  for (let t of r) e = t.connectionString !== void 0 ? t : { ...e, ...t };
  return e;
}
__name(pi, "pi");
a(pi, "mergeConnectionParams");
async function yi(r = "postgresql://-", e = {}, t = {}) {
  if (e.connectionString !== void 0 && (r = e.connectionString), typeof r == "function" && (r = await r()), typeof r != "string") throw new N("Connection string must be a string or a function resolving to one");
  if (e.user !== void 0 && e.username !== void 0) throw new N("Please specify one only of user and username");
  if (e.host !== void 0 && e.hostname !== void 0) throw new N("Please specify one only of host and hostname");
  let n = di(r, false);
  await Promise.all(_a.map(async (u) => {
    if (u === "connectionString") return;
    let c = e[u];
    if (typeof c == "function" && (c = await c()), c === void 0) return;
    if (typeof c != "string" && !(u === "port" && typeof c == "number")) {
      let f = u === "port" ? " or a number" : "";
      throw new N(`Connection parameter "${u}" must be a string${f} or a function resolving to one`);
    }
    let l = Ta[u] ?? u;
    n[l] = c;
  }));
  let { searchParams: i } = n;
  for (let u in t) i.has(u) || i.append(u, t[u]);
  let s = Ca(n), o = di(s, true);
  return { resolvedConnectionString: s, resolvedURL: o };
}
__name(yi, "yi");
a(yi, "resolveConnectionParams");
Ge();
h();
var vt = "pkg:npm/%40neondatabase/serverless@1.2.0";
var ds = we(_t());
var ps = we(rt());
var ls = "transaction() expects an array of queries, or a function returning an array of queries";
function Nu(r) {
  return r instanceof p ? "\\x" + fi(r) : r;
}
__name(Nu, "Nu");
a(Nu, "encodeBuffersAsBytea");
function fs(r) {
  let { query: e, params: t } = r instanceof He ? r.toParameterizedQuery() : r;
  return { query: e, params: t.map((n) => Nu((0, ps.prepareValue)(n))) };
}
__name(fs, "fs");
a(fs, "prepareQuery");
function ys(r, e = {}) {
  typeof r != "string" && (e = r ?? {}, r = void 0);
  let {
    arrayMode: t,
    fullResults: n,
    fetchOptions: i,
    isolationLevel: s,
    readOnly: o,
    deferrable: u,
    authToken: c,
    disableWarningInBrowsers: l
  } = e;
  function f(g, ...w) {
    if (!(Array.isArray(g) && Array.isArray(g.raw) && Array.isArray(w))) throw new Error('This function can now be called only as a tagged-template function: sql`SELECT ${value}`, not sql("SELECT $1", [value], options). For a conventional function call with value placeholders ($1, $2, etc.), use sql.query("SELECT $1", [value], options).');
    return new xe(m, new He(g, w));
  }
  __name(f, "f");
  a(f, "templateFn"), f.query = (g, w, S) => new xe(
    m,
    { query: g, params: w ?? [] },
    S
  ), f.unsafe = (g) => new $e(g), f.transaction = async (g, w) => {
    if (typeof g == "function" && (g = g(f)), !Array.isArray(g)) throw new Error(ls);
    g.forEach((D) => {
      if (!(D instanceof xe)) throw new Error(ls);
    });
    let S = g.map((D) => D.queryData), k = g.map((D) => D.opts ?? {});
    return m(S, k, w);
  };
  async function m(g, w, S) {
    let {
      fetchEndpoint: k,
      fetchFunction: D
    } = pe, he = Array.isArray(g) ? { queries: g.map((G) => fs(G)) } : fs(g), I = i ?? {}, C = t ?? false, re = n ?? false, ne = s, H = o, oe = u;
    S !== void 0 && (S.fetchOptions !== void 0 && (I = { ...I, ...S.fetchOptions }), S.arrayMode !== void 0 && (C = S.arrayMode), S.fullResults !== void 0 && (re = S.fullResults), S.isolationLevel !== void 0 && (ne = S.isolationLevel), S.readOnly !== void 0 && (H = S.readOnly), S.deferrable !== void 0 && (oe = S.deferrable)), w !== void 0 && !Array.isArray(
      w
    ) && w.fetchOptions !== void 0 && (I = { ...I, ...w.fetchOptions });
    let ae = c;
    !Array.isArray(w) && w?.authToken !== void 0 && (ae = w.authToken);
    let me = pi(e, S ?? {}, Array.isArray(w) || !w ? {} : w), { resolvedConnectionString: R, resolvedURL: $ } = await yi(
      r,
      me,
      { application_name: vt }
    ), Ee = typeof k == "function" ? k($.hostname, $.port, { jwtAuth: ae !== void 0 }) : k, ue = {
      "Neon-Connection-String": R,
      "Neon-Raw-Text-Output": "true",
      "Neon-Array-Mode": "true"
    }, Te = await Wu(ae);
    Te && (ue.Authorization = `Bearer ${Te}`), Array.isArray(g) && (ne !== void 0 && (ue["Neon-Batch-Isolation-Level"] = ne), H !== void 0 && (ue["Neon-Batch-Read-Only"] = String(H)), oe !== void 0 && (ue["Neon-Batch-Deferrable"] = String(
      oe
    ))), l || pe.disableWarningInBrowsers || gt();
    let ce;
    try {
      ce = await (D ?? fetch)(Ee, { method: "POST", body: JSON.stringify(he), headers: ue, ...I });
    } catch (G) {
      let q = new N(`Error connecting to database: ${G}`);
      throw q.sourceError = G, q;
    }
    if (ce.ok) {
      let G = await ce.json();
      if (Array.isArray(g)) {
        let q = G.results;
        if (!Array.isArray(q)) throw new N(
          "Neon internal error: unexpected result format"
        );
        return q.map((ge, J) => {
          let ie = w[J] ?? {}, Dt = ie.arrayMode ?? C, Io = ie.fullResults ?? re;
          return hs(ge, { arrayMode: Dt, fullResults: Io, types: ie.types });
        });
      } else {
        let q = w ?? {}, ge = q.arrayMode ?? C, J = q.fullResults ?? re;
        return hs(G, { arrayMode: ge, fullResults: J, types: q.types });
      }
    } else {
      let { status: G } = ce;
      if (G === 400) {
        let q = await ce.json(), ge = new N(q.message);
        for (let J of hi) ge[J] = q[J] ?? void 0;
        throw ge;
      } else {
        let q = await ce.text();
        throw new N(`Server error (HTTP status ${G}): ${q}`);
      }
    }
  }
  __name(m, "m");
  return a(
    m,
    "execute"
  ), f;
}
__name(ys, "ys");
a(ys, "neon");
function hs(r, { arrayMode: e, fullResults: t, types: n }) {
  let i = new ds.default(
    n
  ), s = r.fields.map((c) => c.name), o = r.fields.map((c) => i.getTypeParser(c.dataTypeID)), u = e === true ? r.rows.map((c) => c.map((l, f) => l === null ? null : o[f](l))) : r.rows.map((c) => Object.fromEntries(c.map((l, f) => [s[f], l === null ? null : o[f](l)])));
  return t ? (r.viaNeonFetch = true, r.rowAsArray = e, r.rows = u, r._parsers = o, r._types = i, r) : u;
}
__name(hs, "hs");
a(hs, "processQueryResult");
async function Wu(r) {
  if (typeof r == "string") return r;
  if (typeof r == "function") try {
    return await Promise.resolve(r());
  } catch (e) {
    let t = new N("Error getting auth token.");
    throw e instanceof Error && (t = new N(`Error getting auth token: ${e.message}`)), t;
  }
}
__name(Wu, "Wu");
a(Wu, "getAuthToken");
h();
h();
var Co = we(ot());
h();
var Ao = we(ot());
var On = class On2 extends Ao.Client {
  static {
    __name(this, "On");
  }
  constructor(t) {
    let n = typeof t == "string" ? { connectionString: t } : {
      ...t,
      ...t && "password" in t ? { password: t.password } : {}
    };
    super({ fallback_application_name: vt, ...n });
    E(this, "config", t);
  }
  get neonConfig() {
    return this.connection.stream;
  }
  connect(t) {
    let { neonConfig: n } = this;
    n.forceDisablePgSSL && (this.ssl = this.connection.ssl = false), this.ssl && n.useSecureWebSocket && console.warn("SSL is enabled for both Postgres (e.g. ?sslmode=require in the connection string + forceDisablePgSSL = false) and the WebSocket tunnel (useSecureWebSocket = true). Double encryption will increase latency and CPU usage. It may be appropriate to disable SSL in the Postgres connection parameters or set forceDisablePgSSL = true.");
    let i = typeof this.config != "string" && this.config?.host !== void 0 || typeof this.config != "string" && this.config?.connectionString !== void 0 || y.env.PGHOST !== void 0, s = y.env.USER ?? y.env.USERNAME;
    if (!i && this.host === "localhost" && this.user === s && this.database === s && this.password === null) throw new Error(`No database host or connection string was set, and key parameters have default values (host: localhost, user: ${s}, db: ${s}, password: null). Is an environment variable missing? Alternatively, if you intended to connect with these parameters, please set the host to 'localhost' explicitly.`);
    let o = super.connect(
      t
    ), u = n.pipelineTLS && this.ssl, c = n.pipelineConnect === "password";
    if (!u && !n.pipelineConnect) return o;
    let l = this.connection;
    if (u && l.on("connect", () => l.stream.emit("data", "S")), c) {
      l.removeAllListeners("authenticationCleartextPassword"), l.removeAllListeners("readyForQuery"), l.once("readyForQuery", () => l.on("readyForQuery", this._handleReadyForQuery.bind(this)));
      let f = this.password, m = Promise.resolve(typeof f == "function" ? f() : f), g = this.ssl ? "sslconnect" : "connect";
      l.on(g, () => {
        this.neonConfig.disableWarningInBrowsers || gt(), m.then((w) => {
          this.password = w, this._handleAuthCleartextPassword(), this._handleReadyForQuery();
        }).catch(
          (w) => l.emit("error", w)
        );
      });
    }
    return o;
  }
  async _handleAuthSASLContinue(t) {
    if (typeof crypto > "u" || crypto.subtle === void 0 || crypto.subtle.importKey === void 0) throw new Error("Cannot use SASL auth when `crypto.subtle` is not defined");
    let n = crypto.subtle, i = this.saslSession, s = this.password, o = t.data;
    if (i.message !== "SASLInitialResponse" || typeof s != "string" || typeof o != "string") throw new Error("SASL: protocol error");
    let u = Object.fromEntries(o.split(",").map((J) => {
      if (!/^.=/.test(J)) throw new Error("SASL: Invalid attribute pair entry");
      let ie = J[0], Dt = J.substring(2);
      return [ie, Dt];
    })), c = u.r, l = u.s, f = u.i;
    if (!c || !/^[!-+--~]+$/.test(c))
      throw new Error("SASL: SCRAM-SERVER-FIRST-MESSAGE: nonce missing/unprintable");
    if (!l || !/^(?:[a-zA-Z0-9+/]{4})*(?:[a-zA-Z0-9+/]{2}==|[a-zA-Z0-9+/]{3}=)?$/.test(l)) throw new Error("SASL: SCRAM-SERVER-FIRST-MESSAGE: salt missing/not base64");
    if (!f || !/^[1-9][0-9]*$/.test(f)) throw new Error("SASL: SCRAM-SERVER-FIRST-MESSAGE: missing/invalid iteration count");
    if (!c.startsWith(
      i.clientNonce
    )) throw new Error("SASL: SCRAM-SERVER-FIRST-MESSAGE: server nonce does not start with client nonce");
    if (c.length === i.clientNonce.length) throw new Error("SASL: SCRAM-SERVER-FIRST-MESSAGE: server nonce is too short");
    let m = parseInt(f, 10), g = p.from(l, "base64"), w = new TextEncoder(), S = w.encode(s), k = await n.importKey("raw", S, { name: "HMAC", hash: { name: "SHA-256" } }, false, ["sign"]), D = new Uint8Array(await n.sign("HMAC", k, p.concat([g, p.from([0, 0, 0, 1])]))), he = D;
    for (var I = 0; I < m - 1; I++) D = new Uint8Array(await n.sign("HMAC", k, D)), he = p.from(he.map((J, ie) => he[ie] ^ D[ie]));
    let C = he, re = await n.importKey("raw", C, { name: "HMAC", hash: { name: "SHA-256" } }, false, ["sign"]), ne = new Uint8Array(await n.sign("HMAC", re, w.encode("Client Key"))), H = await n.digest("SHA-256", ne), oe = "n=*,r=" + i.clientNonce, ae = "r=" + c + ",s=" + l + ",i=" + m, me = "c=biws,r=" + c, R = oe + "," + ae + "," + me, $ = await n.importKey("raw", H, { name: "HMAC", hash: { name: "SHA-256" } }, false, ["sign"]);
    var Ee = new Uint8Array(await n.sign("HMAC", $, w.encode(R))), ue = p.from(ne.map((J, ie) => ne[ie] ^ Ee[ie])), Te = ue.toString("base64");
    let ce = await n.importKey("raw", C, { name: "HMAC", hash: { name: "SHA-256" } }, false, ["sign"]), G = await n.sign("HMAC", ce, w.encode("Server Key")), q = await n.importKey("raw", G, { name: "HMAC", hash: { name: "SHA-256" } }, false, ["sign"]);
    var ge = p.from(await n.sign("HMAC", q, w.encode(R)));
    i.message = "SASLResponse", i.serverSignature = ge.toString("base64"), i.response = me + ",p=" + Te, this.connection.sendSCRAMClientFinalMessage(
      this.saslSession.response
    );
  }
};
a(On, "NeonClient");
var ut = On;
Ge();
var _o = we(Lt());
function Wl(r, e) {
  if (e) return { callback: e, result: void 0 };
  let t, n, i = a(function(o, u) {
    o ? t(o) : n(u);
  }, "cb"), s = new r(function(o, u) {
    n = o, t = u;
  });
  return { callback: i, result: s };
}
__name(Wl, "Wl");
a(Wl, "promisify");
var Qn = class Qn2 extends Co.Pool {
  static {
    __name(this, "Qn");
  }
  constructor() {
    super(...arguments);
    E(this, "Client", ut);
    E(this, "hasFetchUnsupportedListeners", false);
    E(this, "addListener", this.on);
  }
  on(t, n) {
    return t !== "error" && (this.hasFetchUnsupportedListeners = true), super.on(t, n);
  }
  query(t, n, i) {
    if (!pe.poolQueryViaFetch || this.hasFetchUnsupportedListeners || typeof t == "function") return super.query(
      t,
      n,
      i
    );
    typeof n == "function" && (i = n, n = void 0);
    let s = Wl(this.Promise, i);
    i = s.callback;
    try {
      let o = new _o.default(
        this.options
      ), u = encodeURIComponent, c = encodeURI, l = `postgresql://${u(o.user)}:${u(o.password)}@${u(o.host)}/${c(o.database)}`, f = typeof t == "string" ? t : t.text, m = n ?? t.values ?? [];
      ys(l, { fullResults: true, arrayMode: t.rowMode === "array" }).query(f, m, { types: t.types ?? this.options?.types }).then((w) => i(void 0, w)).catch((w) => i(
        w
      ));
    } catch (o) {
      i(o);
    }
    return s.result;
  }
};
a(Qn, "NeonPool");
Ge();
var ct = we(ot());
h();
var To = we(Ir());
function jl(r) {
  return Object.entries(r).reduce((t, [n, i]) => (i != null && (t[n] = i), t), /* @__PURE__ */ Object.create(null));
}
__name(jl, "jl");
a(jl, "toConnectionOptions");
function Hl(r) {
  return Object.entries(r).reduce((t, [n, i]) => {
    if (n === "ssl") {
      let s = i;
      typeof s == "boolean" && (t[n] = s), typeof s == "object" && (t[n] = jl(s));
    } else if (i != null) if (n === "port") {
      if (i !== "") {
        let s = parseInt(i, 10);
        if (isNaN(s)) throw new Error(`Invalid ${n}: ${i}`);
        t[n] = s;
      }
    } else t[n] = i;
    return t;
  }, /* @__PURE__ */ Object.create(null));
}
__name(Hl, "Hl");
a(Hl, "toClientConfig");
function $l(r) {
  return Hl((0, To.parse)(r));
}
__name($l, "$l");
a(
  $l,
  "parseIntoClientConfig"
);
var export_DatabaseError = ct.DatabaseError;
var export_defaults = ct.defaults;
var export_escapeIdentifier = ct.escapeIdentifier;
var export_escapeLiteral = ct.escapeLiteral;
var export_types = ct.types;

// src/neon-adapter.js
var isoDate = /* @__PURE__ */ __name((v2) => v2 instanceof Date ? v2.toISOString().slice(0, 10) : String(v2).slice(0, 10), "isoDate");
var id = /* @__PURE__ */ __name((v2) => String(v2 ?? ""), "id");
var amount = /* @__PURE__ */ __name((v2) => Number.isFinite(Number(v2)) ? Number(v2) : 0, "amount");
var marker = " ||APROAR_META|| ";
function metadata(observation) {
  const [text, ...rest] = String(observation || "").split(marker);
  let meta = {};
  if (rest.length) {
    try {
      meta = JSON.parse(rest.join(marker));
    } catch {
    }
  }
  return { text, meta };
}
__name(metadata, "metadata");
var extraLabel = /* @__PURE__ */ __name((value2, base) => {
  const ratio = base > 0 ? amount(value2) / base : 0;
  return ratio === 0 ? "N\xE3o" : Math.abs(ratio - 0.5) < 0.02 ? "Meia di\xE1ria" : Math.abs(ratio - 1) < 0.02 ? "Di\xE1ria" : Math.abs(ratio - 1.5) < 0.02 ? "Uma e meia di\xE1ria" : Math.abs(ratio - 2) < 0.02 ? "Duas di\xE1rias" : "Valor espec\xEDfico";
}, "extraLabel");
function mapNeonData(db) {
  const colaboradores = (db.colaboradores || []).map((p2) => ({ id: id(p2.id), nome: p2.nome, funcao: p2.funcao, custo: amount(p2.valor_diaria), moradia: p2.local_moradia || "", inativo: p2.ativo === false, categoria: p2.categoria_diaria || "", avulso: p2.avulso || "N\xE3o" }));
  const obras = (db.obras || []).map((o) => ({ id: id(o.id), nome: o.nome, unidade: o.unidade }));
  const people = new Map(colaboradores.map((p2) => [p2.id, p2])), works = new Map(obras.map((o) => [o.id, o])), worksByName = new Map(obras.map((o) => [o.nome, o]));
  const pointed = new Map((db.apontamentos || []).map((a2) => [id(a2.convocacao_id), a2]));
  const services = /* @__PURE__ */ new Map();
  for (const s of db.servicos_apontamento || []) {
    const key2 = id(s.convocacao_id);
    if (!services.has(key2)) services.set(key2, []);
    services.get(key2).push(s);
  }
  const convocacoes = [], apontamentos = [], extras = [], warnings = [];
  for (const c of db.convocacoes || []) {
    const key2 = id(c.id), work = id(c.obra_id), { text, meta } = metadata(c.observacao);
    const eventAvulso = meta.avulso_eventual;
    const person = eventAvulso?.id ? String(eventAvulso.id) : id(c.colaborador_id);
    if (eventAvulso?.id && !people.has(person)) {
      const temporary = {
        id: person,
        nome: String(eventAvulso.nome || "Avulso"),
        funcao: String(eventAvulso.funcao || "Profissional"),
        custo: amount(eventAvulso.custo),
        categoria: String(eventAvulso.categoria || ""),
        moradia: "",
        inativo: true,
        avulso: "Sim",
        avulsoRegistro: true
      };
      people.set(person, temporary);
      colaboradores.push(temporary);
    }
    if (!person) continue;
    const turno = c.turno || text.match(/Turno:\s*(Integral|Manhã|Tarde|Noite)/i)?.[1] || "Integral";
    const a2 = pointed.get(key2);
    if (meta.extra_avulsa === true) {
      if (meta.extra_cancelada === true) continue;
      if (!a2) continue;
      const cost2 = people.get(person)?.custo || 0, extra2 = amount(a2.valor_extra ?? c.valor_extra), targetWork = id(meta.extra_obra_id || work);
      const savedType2 = ["N\xE3o", "Meia di\xE1ria", "Di\xE1ria", "Uma e meia di\xE1ria", "Duas di\xE1rias"].includes(a2.tipo_diaria) ? a2.tipo_diaria : null;
      extras.push({ id: key2, supervisor: c.engenheiro, dataServico: isoDate(c.data), unidade: works.get(targetWork)?.unidade || meta.extra_unidade || works.get(work)?.unidade || "", obraId: targetWork, colaboradorId: person, extra: savedType2 || extraLabel(extra2, cost2), valorExtraOriginal: extra2, observacao: String(meta.extra_observacao || a2.observacao || ""), criadoEm: a2.apontado_em || meta.extra_lancado_em || c.criado_em || null, executor: a2.apontado_por || meta.extra_lancado_por || c.engenheiro, servicoDiaId: id(meta.extra_dia_obra_id || "") });
      continue;
    }
    convocacoes.push({ id: key2, supervisor: c.engenheiro, dataServico: isoDate(c.data), unidade: meta.unidade_convocada || works.get(work)?.unidade || "", obraId: meta.servico_a_definir ? "" : work, turno, colaboradores: [person], criadoEm: c.criado_em || meta.convocado_em || null, executor: c.criado_por || meta.convocado_por || c.engenheiro, origem: "neon" });
    if (!a2 && !meta.apontado_em && c.custos_separados !== true) continue;
    const source = a2 || c, raw = (services.get(key2) || []).slice().sort((a,b)=>
      Number(b.principal)-Number(a.principal)||Number(a.id)-Number(b.id)), additional = meta.servicos_adicionais || [];
    // As tabelas guardam o vínculo da obra; a classificação e a independência
    // da extra permanecem no metadado estruturado da convocação.
    const readExtraForService = (obraId, periodo) => additional.find(s =>
      String(s.obra_id || "") === String(obraId) &&
      String(s.periodo || turno) === String(periodo || turno));
    const mapped = raw.length ? raw.map((s) => {
      const obraId=id(s.obra_id) || worksByName.get(s.obra_nome_snapshot)?.id || "",periodo=s.periodo||turno;
      const details=Boolean(s.principal)?null:readExtraForService(obraId,periodo);
      return {obraId,periodo,extra:details?.extra||"Não",extraIndependente:details?.extra_independente===true};
    }) : [
      {obraId:work,periodo:meta.periodo_principal||turno,extra:"Não",extraIndependente:false},
      ...additional.map(s=>({obraId:id(s.obra_id)||worksByName.get(s.servico)?.id||"",periodo:s.periodo||turno,extra:s.extra||"Não",extraIndependente:s.extra_independente===true}))
    ];
    if (mapped.some((s) => !s.obraId)) warnings.push({ code: "UNMAPPED_SERVICE", convocacaoId: key2 });
    const cost = people.get(person)?.custo || 0, extra = amount(source.valor_extra), savedType = ["N\xE3o", "Meia di\xE1ria", "Di\xE1ria", "Uma e meia di\xE1ria", "Duas di\xE1rias"].includes(source.tipo_diaria) ? source.tipo_diaria : null;
    if (extra && extraLabel(extra, cost) === "Valor espec\xEDfico") warnings.push({ code: "NONSTANDARD_EXTRA", convocacaoId: key2, value: extra });
    apontamentos.push({ id: a2 ? id(a2.id) : "legacy-" + key2, convocacaoId: key2, supervisor: c.engenheiro, dataServico: isoDate(c.data), apontadoEm: a2?.apontado_em || meta.apontado_em || null, executor: a2?.apontado_por || meta.apontado_por || c.engenheiro, retroativo: a2?.retroativo || meta.apontamento_atrasado || false, itens: [{ colaboradorId: person, status: source.status === "Extra" ? "Presente (Integral)" : source.status, extra: savedType || extraLabel(extra, cost), valorExtraOriginal: extra, valorExtraDisponivel: amount(meta.valor_extra_disponivel ?? extra), observacao: a2?.observacao || text.replace(/^Turno:[^|]+\|?\s*/, ""), financeiro: amount(source.custo_pago ?? meta.custo_pago), confirmacaoComplemento: meta.aprovacao_complemento_igual_acordo || null, financeAdjusted: source.custo_pago_definido_financeiro === true, tipoDiariaAvulso: people.get(person)?.avulso === "Sim" ? ["Meia di\xE1ria", "Di\xE1ria", "Uma e meia di\xE1ria", "Duas di\xE1rias"].includes(meta.tipo_diaria_avulso) ? meta.tipo_diaria_avulso : "Di\xE1ria" : null, noturno: amount(source.valor_adicional_noturno ?? meta.valor_adicional_noturno), acordo: amount(source.valor_acordo ?? meta.valor_acordo), ajudaCusto: amount(meta.valor_ajuda_custo), tipoDiariaOriginal: source.tipo_diaria, servicos: mapped, custoEncargosOriginal: source.custo_encargos_base }] });
  }
  return {
    colaboradores,
    obras,
    convocacoes,
    apontamentos,
    extras,
    warnings,
    indisponibilidades: (db.indisponibilidades || []).filter((x2) => x2.ativo).map((x2) => ({ id: id(x2.id), colaboradorId: id(x2.colaborador_id), motivo: x2.motivo, inicio: isoDate(x2.inicio), fim: isoDate(x2.fim), observacao: x2.observacao || "", obs: x2.observacao || "" })),
    conflitosTentados: (db.conflitos_convocacao || []).map((x2) => ({ id: id(x2.id), colaboradorId: id(x2.colaborador_id), colaboradorNome: x2.colaborador_nome_snapshot, dataServico: isoDate(x2.data), supervisor: x2.engenheiro_tentativa, unidade: x2.unidade_tentativa, turno: x2.turno_tentativa, supervisorExistente: x2.engenheiro_original, unidadeExistente: x2.unidade_original, turnoExistente: x2.turno_original, convocacaoExistenteId: id(x2.convocacao_existente_id), data: x2.criado_em, resolvido: x2.resolvido, conferidoEm: x2.resolvido_em })),
    auditoria: (db.auditoria || []).map((x2) => ({ id: id(x2.id), data: x2.ocorrido_em, usuario: x2.usuario, action: x2.acao, ref: x2.entidade + " " + (x2.entidade_id || "") }))
  };
}
__name(mapNeonData, "mapNeonData");

// src/unit-label.js
function isSafeUnitName(value2) {
  return typeof value2 === "string" && value2.trim().length > 0 && value2.trim().length <= 80 && !/(?:https?:\/\/|www\.|sharepoint|link\s+para\s+acesso)/i.test(value2);
}
__name(isSafeUnitName, "isSafeUnitName");

// src/data.js
var supervisors = ["EDUARDO", "FELIPE", "GABRIEL", "JOEL", "NETO", "SOARES", "VICTOR", "DJOUNE XAVIER"];
async function readDatabase(sql, { auditUser = null, includeAudit = true } = {}) {
  const names = ["colaboradores", "obras", "convocacoes", "apontamentos", "servicos_apontamento", "indisponibilidades", "conflitos_convocacao", "auditoria", "engenheiros_teams", "cobrancas_teams", "settings", "version"];
  const auditQuery = !includeAudit ? sql`SELECT id,entidade,entidade_id,acao,usuario,ocorrido_em FROM auditoria WHERE false` : auditUser ? sql`SELECT id,entidade,entidade_id,acao,usuario,ocorrido_em FROM auditoria WHERE usuario=${auditUser} ORDER BY id` : sql`SELECT id,entidade,entidade_id,acao,usuario,ocorrido_em FROM auditoria ORDER BY id`;
  const result = await sql.transaction([sql`SELECT * FROM colaboradores ORDER BY id`, sql`SELECT * FROM obras ORDER BY id`, sql`SELECT * FROM convocacoes ORDER BY id`, sql`SELECT * FROM apontamentos ORDER BY id`, sql`SELECT * FROM servicos_apontamento ORDER BY id`, sql`SELECT * FROM indisponibilidades ORDER BY id`, sql`SELECT * FROM conflitos_convocacao ORDER BY id`, auditQuery, sql`SELECT * FROM engenheiros_teams ORDER BY engenheiro`, sql`SELECT * FROM cobrancas_teams ORDER BY id`, sql`SELECT data FROM aproar_web_settings WHERE id=1`, sql`SELECT aproar_web_fingerprint() AS version`], { isolationLevel: "RepeatableRead", readOnly: true });
  const raw = Object.fromEntries(names.map((n, i) => [n, result[i]])), state = mapNeonData(raw);
  const config = raw.settings[0]?.data || {};
  Object.assign(state, { units: [...new Set([...Array.isArray(config.units) ? config.units : [], ...state.obras.map((o) => o.unidade)].filter(isSafeUnitName))].sort((a2, b2) => a2.localeCompare(b2, "pt-BR")), unitOwners: config.unitOwners || {}, semConvocacoesUnidade: Array.isArray(config.semConvocacoesUnidade) ? config.semConvocacoesUnidade : [], dispensasPendenciaConvocacao: Array.isArray(config.dispensasPendenciaConvocacao) ? config.dispensasPendenciaConvocacao : [], dispensasPendenciaApontamento: Array.isArray(config.dispensasPendenciaApontamento) ? config.dispensasPendenciaApontamento : [], teamsAutomation: config.teamsAutomation || false, teamsMessage: config.teamsMessage || "", teamsHistory: [...(raw.cobrancas_teams || []).map((x2) => ({ id: String(x2.id), data: x2.enviado_em, supervisor: x2.engenheiro, quantidade: x2.qtd_pendentes, status: x2.status, detalhe: x2.mensagem })), ...config.teamsHistory || []] });
  state.teamsConfig = Object.fromEntries(raw.engenheiros_teams.map((x2) => [x2.engenheiro, { email: x2.email_teams || "", ativo: x2.ativo }]));
  return { raw, state, version: raw.version[0].version };
}
__name(readDatabase, "readDatabase");
function visibleState(db, session) {
  const state = session.role === "CONTROLADORIA" ? db.state : structuredClone(db.state);
  if (session.role !== "CONTROLADORIA") state.dispensasPendenciaConvocacao = (state.dispensasPendenciaConvocacao || []).map((x2) => ({ supervisor: x2.supervisor, dataServico: x2.dataServico }));
  if (session.role !== "CONTROLADORIA") state.dispensasPendenciaApontamento = (state.dispensasPendenciaApontamento || []).map((x2) => ({ supervisor: x2.supervisor, dataServico: x2.dataServico }));
  if (session.role === "SUPERVISOR") {
    state.apontamentos = state.apontamentos.filter((a2) => a2.supervisor === session.user);
    state.extras = (state.extras || []).filter((x2) => x2.supervisor === session.user);
    state.auditoria = state.auditoria.filter((a2) => a2.usuario === session.user);
    state.teamsConfig = {};
    state.teamsHistory = [];
    state.teamsMessage = "";
  }
  return state;
}
__name(visibleState, "visibleState");

// src/financial-history.js
var fields = [
  { column: "valor_extra", type: "Extra" },
  { column: "valor_acordo", type: "Bonifica\xE7\xE3o / acordo" },
  { column: "valor_adicional_noturno", type: "Adicional noturno" }
];
var value = /* @__PURE__ */ __name((n) => Math.round((Number(n) || 0) * 100) / 100, "value");
function financialHistoryEvents({ convocationId, colaboradorId, dataServico, supervisor, actor, role, source, timestamp, previous, next }) {
  const events = [];
  for (const f of fields) {
    const before = value(previous?.[f.column]), after = value(next?.[f.column]);
    if (before === after) continue;
    events.push({
      table: "auditoria",
      action: "insert",
      id: "audit:" + crypto.randomUUID(),
      data: {
        entidade: "apontamentos",
        entidade_id: String(convocationId),
        acao: "LANCAMENTO_FINANCEIRO_ITEM",
        usuario: actor,
        ocorrido_em: timestamp,
        antes: { valor: before },
        depois: { valor: after },
        contexto: {
          versao: 1,
          convocacaoId: String(convocationId),
          colaboradorId: String(colaboradorId),
          dataServico: String(dataServico),
          supervisorResponsavel: String(supervisor || ""),
          usuarioResponsavel: String(actor),
          perfil: String(role),
          origem: String(source),
          tipo: f.type,
          campo: f.column,
          valorAnterior: before,
          valorNovo: after,
          operacao: before === 0 && after > 0 ? "Inclus\xE3o" : after === 0 ? "Remo\xE7\xE3o" : "Altera\xE7\xE3o"
        }
      }
    });
  }
  return events;
}
__name(financialHistoryEvents, "financialHistoryEvents");

// src/financial-release.js
var releaseFields = ["Extra", "Bonifica\xE7\xE3o", "Adicional noturno", "Passagem / ajuda de custo", "Complemento financeiro"];
var financialPaymentBundle = ["Extra", "Bonifica\xE7\xE3o", "Passagem / ajuda de custo"];
function authorizedFieldsForApproval(fields2, approvedBy) {
  const original = [...new Set((fields2 || []).filter((x2) => releaseFields.includes(x2)))];
  if (approvedBy !== "FINANCEIRO" || !original.some((x2) => financialPaymentBundle.includes(x2))) return original;
  return [.../* @__PURE__ */ new Set([...original, ...financialPaymentBundle])];
}
__name(authorizedFieldsForApproval, "authorizedFieldsForApproval");
var day = /* @__PURE__ */ __name((v2) => {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(String(v2))) throw Error("Data inv\xE1lida.");
  const d = /* @__PURE__ */ new Date(String(v2) + "T12:00:00Z");
  if (!Number.isFinite(d.valueOf()) || d.toISOString().slice(0, 10) !== v2) throw Error("Data inv\xE1lida.");
  return d;
}, "day");
function financialDeadline(serviceDate) {
  const d = day(serviceDate);
  const sinceMonday = (d.getUTCDay() + 6) % 7;
  const start = new Date(d);
  start.setUTCDate(start.getUTCDate() - sinceMonday);
  const end = new Date(start);
  end.setUTCDate(end.getUTCDate() + 6);
  const pay = new Date(start);
  pay.setUTCDate(pay.getUTCDate() + 8);
  const payment = pay.toISOString().slice(0, 10);
  return {
    start: start.toISOString().slice(0, 10),
    end: end.toISOString().slice(0, 10),
    payment,
    limitAt: payment + "T10:00:00-03:00"
  };
}
__name(financialDeadline, "financialDeadline");
var afterFinancialDeadline = /* @__PURE__ */ __name((serviceDate, timestamp) => new Date(timestamp).getTime() > new Date(financialDeadline(serviceDate).limitAt).getTime(), "afterFinancialDeadline");
function validRequest(input) {
  if (!input || typeof input !== "object" || !/^(?:\d{1,18}|[a-z][a-z0-9_-]{2,90})$/i.test(String(input.colaboradorId || ""))) throw Error("Colaborador inv\xE1lido.");
  day(input.dataServico);
  if (!Array.isArray(input.fields) || input.fields.length === 0 || input.fields.length > releaseFields.length || new Set(input.fields).size !== input.fields.length || input.fields.some((x2) => !releaseFields.includes(x2))) throw Error("Selecione as colunas que precisam de libera\xE7\xE3o.");
  if (typeof input.reason !== "string" || input.reason.trim().length < 10 || input.reason.trim().length > 600) throw Error("Informe o motivo da solicita\xE7\xE3o (10 a 600 caracteres).");
  return { colaboradorId: String(input.colaboradorId), dataServico: input.dataServico, fields: input.fields.slice(), reason: input.reason.trim() };
}
__name(validRequest, "validRequest");
function releaseState(events) {
  const map = /* @__PURE__ */ new Map();
  for (const e of events) {
    const ctx = e.contexto || {}, rid = ctx.requestId;
    if (!rid) continue;
    if (e.acao === "SOLICITACAO_LIBERACAO_FINANCEIRA") {
      map.set(rid, { id: rid, supervisor: ctx.supervisor, colaboradorId: String(ctx.colaboradorId || ""), colaborador: ctx.colaborador || "", dataServico: ctx.dataServico, fields: ctx.fields || [], reason: ctx.reason, createdAt: e.ocorrido_em, status: "Pendente", approvedBy: null, approvedAt: null, usedAt: null, decisionReason: null });
    } else if (map.has(rid)) {
      const item = map.get(rid);
      if (e.acao === "LIBERACAO_FINANCEIRA_AUTORIZADA" && item.status === "Pendente") {
        item.status = "Autorizada";
        item.approvedBy = e.usuario;
        item.approvedAt = e.ocorrido_em;
        item.requestedFields = item.fields.slice();
        item.fields = authorizedFieldsForApproval(item.fields, e.usuario);
      }
      if (e.acao === "LIBERACAO_FINANCEIRA_NEGADA" && item.status === "Pendente") {
        item.status = "Negada";
        item.decisionReason = ctx.reason || "";
      }
      if (e.acao === "LIBERACAO_FINANCEIRA_UTILIZADA" && item.status === "Autorizada") {
        item.status = "Utilizada";
        item.usedAt = e.ocorrido_em;
      }
    }
  }
  return [...map.values()].reverse();
}
__name(releaseState, "releaseState");
function requireApprovedReleases(events, { supervisor, colaboradorId, dataServico, fields: fields2 }, timestamp, usedIds = /* @__PURE__ */ new Map()) {
  if (!afterFinancialDeadline(dataServico, timestamp) || !fields2.length) return [];
  const person = String(colaboradorId), requested = [...new Set(fields2)];
  const matches = /* @__PURE__ */ __name((x2) => x2.supervisor === supervisor && x2.colaboradorId === person && x2.dataServico === dataServico, "matches");
  const already = usedIds instanceof Map ? [...usedIds.values()].filter(matches) : [];
  const covered = new Set(already.flatMap((x2) => x2.fields || []));
  const selected = [];
  const authorized = releaseState(events || []).filter((x2) => matches(x2) && x2.status === "Autorizada" && !usedIds.has(x2.id));
  for (const grant of authorized) {
    if (!(grant.fields || []).some((f) => requested.includes(f) && !covered.has(f))) continue;
    selected.push(grant);
    for (const field2 of grant.fields || []) covered.add(field2);
    if (requested.every((f) => covered.has(f))) break;
  }
  const missing = requested.filter((f) => !covered.has(f));
  if (missing.length) {
    const permitted = requested.filter((f) => covered.has(f));
    const note = permitted.length ? " As seguintes colunas j\xE1 possuem autoriza\xE7\xE3o e N\xC3O precisam de nova solicita\xE7\xE3o: " + permitted.join(", ") + "." : "";
    throw Object.assign(
      new Error("Prazo financeiro encerrado \xE0s 10h do dia do pagamento. Solicite libera\xE7\xE3o SOMENTE para: " + missing.join(", ") + "." + note),
      { status: 403, details: {
        dataServico,
        colaboradorId: person,
        fields: missing,
        alreadyApproved: permitted,
        limitAt: financialDeadline(dataServico).limitAt
      } }
    );
  }
  const operations = [];
  for (const grant of selected) {
    if (usedIds instanceof Map) usedIds.set(grant.id, { supervisor, colaboradorId: person, dataServico, fields: grant.fields.slice() });
    else usedIds.add(grant.id);
    operations.push({ table: "auditoria", action: "insert", id: "audit:" + crypto.randomUUID(), data: {
      entidade: "apontamentos",
      entidade_id: person,
      acao: "LIBERACAO_FINANCEIRA_UTILIZADA",
      usuario: supervisor,
      ocorrido_em: timestamp,
      contexto: {
        requestId: grant.id,
        supervisor,
        colaboradorId: person,
        dataServico,
        fields: requested.filter((field2) => grant.fields.includes(field2)),
        approvedBy: grant.approvedBy,
        approvedAt: grant.approvedAt
      }
    } });
  }
  return operations;
}
__name(requireApprovedReleases, "requireApprovedReleases");
function changedFinancialFields(current, next) {
  const n = /* @__PURE__ */ __name((v2) => Math.round((Number(v2) || 0) * 100) / 100, "n");
  const result = [];
  if (String(next?.extra || "N\xE3o") !== String(current?.extra || "N\xE3o") || n(next?.valorExtraOriginal) !== n(current?.valorExtraOriginal) || n(next?.valorExtraDisponivel) !== n(current?.valorExtraDisponivel)) result.push("Extra");
  if (n(next?.acordo) !== n(current?.acordo)) result.push("Bonifica\xE7\xE3o");
  if (n(next?.noturno) !== n(current?.noturno)) result.push("Adicional noturno");
  if (n(next?.ajudaCusto) !== n(current?.ajudaCusto)) result.push("Passagem / ajuda de custo");
  if (n(next?.financeiro) !== n(current?.financeiro)) result.push("Complemento financeiro");
  return result;
}
__name(changedFinancialFields, "changedFinancialFields");

// src/financial-approval.js
var invalid = /* @__PURE__ */ __name((message, status = 400) => {
  throw Object.assign(new Error(message), { status });
}, "invalid");
var cents = /* @__PURE__ */ __name((v2) => Math.round(Number(v2) * 100), "cents");
var validAmount = /* @__PURE__ */ __name((v2) => typeof v2 === "number" && Number.isFinite(v2) && v2 > 0 && v2 <= 1e7, "validAmount");
var approvalKey = "aprovacao_complemento_igual_acordo";
function hasValidComplementApproval(meta, financeiro, acordo) {
  const approval = meta?.[approvalKey];
  return Boolean(approval && approval.aprovadoPor === "FINANCEIRO" && typeof approval.aprovadoEm === "string" && approval.aprovadoEm.length >= 19 && typeof approval.justificativa === "string" && approval.justificativa.trim().length >= 10 && Number.isFinite(cents(financeiro)) && cents(financeiro) > 0 && cents(financeiro) === cents(acordo) && cents(approval.financeiro) === cents(financeiro) && cents(approval.acordo) === cents(acordo));
}
__name(hasValidComplementApproval, "hasValidComplementApproval");
function clearObsoleteApproval(meta, financeiro, acordo) {
  const next = { ...meta };
  if (!hasValidComplementApproval(next, financeiro, acordo)) delete next[approvalKey];
  return next;
}
__name(clearObsoleteApproval, "clearObsoleteApproval");
function validateComplementConfirmation(body) {
  if (!body || typeof body !== "object" || Array.isArray(body) || Object.keys(body).some((k) => !["requestId", "version", "convocacaoId", "financeiro", "acordo", "justificativa"].includes(k)))
    invalid("Confirma\xE7\xE3o financeira inv\xE1lida.");
  if (typeof body.requestId !== "string" || !/^[0-9a-f-]{36}$/i.test(body.requestId) || typeof body.version !== "string" || !/^[0-9a-f]{32}$/i.test(body.version))
    invalid("Identificador ou vers\xE3o de confirma\xE7\xE3o inv\xE1lidos.");
  if (!/^[1-9][0-9]{0,17}$/.test(String(body.convocacaoId || "")))
    invalid("Apontamento inv\xE1lido para confirma\xE7\xE3o.");
  if (!validAmount(body.financeiro) || !validAmount(body.acordo) || cents(body.financeiro) !== cents(body.acordo))
    invalid("Confirme apenas valores complementares positivos e iguais aos acordos.");
  if (typeof body.justificativa !== "string" || body.justificativa.trim().length < 10 || body.justificativa.trim().length > 400)
    invalid("Descreva por que s\xE3o dois pagamentos distintos (m\xEDnimo de 10 caracteres, m\xE1ximo de 400).");
  return {
    ...body,
    convocacaoId: String(body.convocacaoId),
    financeiro: cents(body.financeiro) / 100,
    acordo: cents(body.acordo) / 100,
    justificativa: body.justificativa.trim()
  };
}
__name(validateComplementConfirmation, "validateComplementConfirmation");
function buildComplementConfirmationOperations(body, record, actor, timestamp = (/* @__PURE__ */ new Date()).toISOString()) {
  if (actor !== "FINANCEIRO") invalid("Somente o Financeiro pode confirmar pagamentos complementares.", 403);
  if (!record || String(record.convocacao_id) !== body.convocacaoId || !record.apontamento_id)
    invalid("Apontamento n\xE3o localizado. Atualize os dados.", 409);
  if (["Falta", "Atestado"].includes(record.status))
    invalid("N\xE3o \xE9 poss\xEDvel aprovar pagamento de falta ou atestado.");
  if (cents(record.acordo_atual) !== cents(body.acordo) || cents(record.acordo_convocacao) !== cents(body.acordo))
    invalid("O valor do acordo mudou. Atualize a tela antes de confirmar.", 409);
  if (cents(record.complemento_atual) !== cents(record.complemento_convocacao))
    invalid("O complemento possui diferen\xE7as entre os registros; solicite revis\xE3o antes de aprovar.", 409);
  const { text, meta } = metadata(record.observacao);
  if (hasValidComplementApproval(meta, body.financeiro, body.acordo))
    invalid("Esses valores j\xE1 foram confirmados pelo Financeiro.", 409);
  const approval = {
    aprovadoPor: actor,
    aprovadoEm: timestamp,
    justificativa: body.justificativa,
    financeiro: body.financeiro,
    acordo: body.acordo,
    convocacaoId: body.convocacaoId
  };
  const nextMeta = { ...meta, custo_pago: body.financeiro, [approvalKey]: approval };
  return [
    { table: "apontamentos", action: "update", id: String(record.apontamento_id), data: {
      custo_pago: body.financeiro,
      custo_pago_definido_financeiro: true,
      atualizado_em: timestamp
    } },
    { table: "convocacoes", action: "update", id: body.convocacaoId, data: {
      custo_pago: body.financeiro,
      custo_pago_definido_financeiro: true,
      observacao: text + " ||APROAR_META|| " + JSON.stringify(nextMeta)
    } },
    { table: "auditoria", action: "insert", id: "approval:" + crypto.randomUUID(), data: {
      entidade: "apontamentos",
      entidade_id: String(record.apontamento_id),
      acao: "CONFIRMAR_COMPLEMENTO_DUPLICADO",
      usuario: actor,
      ocorrido_em: timestamp,
      contexto: {
        convocacaoId: body.convocacaoId,
        financeiro: body.financeiro,
        acordo: body.acordo,
        justificativa: body.justificativa,
        aprovadoEm: timestamp
      }
    } }
  ];
}
__name(buildComplementConfirmationOperations, "buildComplementConfirmationOperations");

// src/operations.js
var numericId = /* @__PURE__ */ __name((v2) => /^\d+$/.test(String(v2)), "numericId");
var clean = /* @__PURE__ */ __name((v2) => String(v2 || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toUpperCase().trim(), "clean");
var money = /* @__PURE__ */ __name((v2) => Math.round(Number(v2) * 100) / 100, "money");
var same = /* @__PURE__ */ __name((a2, b2) => JSON.stringify(a2) === JSON.stringify(b2), "same");
var field = /* @__PURE__ */ __name((o, keys) => Object.fromEntries(keys.map((k) => [k, o?.[k] ?? null])), "field");
var fail = /* @__PURE__ */ __name((message, status = 400, details) => {
  throw Object.assign(Error(message), { status, details });
}, "fail");
var finite = /* @__PURE__ */ __name((v2) => Number.isFinite(Number(v2)) && Number(v2) >= 0 && Number(v2) <= 1e7, "finite");
var required = /* @__PURE__ */ __name((s, label) => {
  if (typeof s !== "string" || !s.trim() || s.length > 2e3) fail(label + " inv\xE1lido.");
  return s.trim();
}, "required");
var date = /* @__PURE__ */ __name((d) => {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(d) || (/* @__PURE__ */ new Date(d + "T12:00:00Z")).toISOString().slice(0, 10) !== d) fail("Data inv\xE1lida.");
  return d;
}, "date");
var period = /* @__PURE__ */ __name((p2) => {
  if (!["Manh\xE3", "Tarde", "Noite", "Integral"].includes(p2)) fail("Escolha um turno v\xE1lido.");
  return p2;
}, "period");
var present = /* @__PURE__ */ __name((s) => !["Falta", "Atestado"].includes(s), "present");
var mult = /* @__PURE__ */ __name((e) => ({ "N\xE3o": 0, "Meia di\xE1ria": 0.5, "Di\xE1ria": 1, "Uma e meia di\xE1ria": 1.5, "Duas di\xE1rias": 2 })[e], "mult");
var editableAp = ["status", "extra", "observacao", "servicos", "financeiro", "noturno", "acordo", "ajudaCusto", "tipoDiariaAvulso", "valorExtraDisponivel"];
var avulsoDailyTypes = ["Meia di\xE1ria", "Di\xE1ria", "Uma e meia di\xE1ria", "Duas di\xE1rias"];
var pendingAvulsoInvalid = /* @__PURE__ */ __name((i, p2) => i.tipoDiariaAvulso != null && (!p2 || p2.avulso !== "Sim" || !avulsoDailyTypes.includes(i.tipoDiariaAvulso)), "pendingAvulsoInvalid");
var normServices = /* @__PURE__ */ __name((i) => (i?.servicos || []).map((s, index) => ({
  obraId: String(s.obraId || ""),
  periodo: s.periodo || "Integral",
  extra: index > 0 ? String(s.extra || "Não") : "Não",
  extraIndependente: index > 0 && s.extraIndependente === true
})), "normServices");
var apView = /* @__PURE__ */ __name((i) => ({ ...field(i, editableAp), ajudaCusto: Number(i?.ajudaCusto) || 0, servicos: normServices(i) }), "apView");
var overlap = /* @__PURE__ */ __name((a2, b2) => a2 === b2 || a2 === "Integral" && ["Manh\xE3", "Tarde"].includes(b2) || b2 === "Integral" && ["Manh\xE3", "Tarde"].includes(a2), "overlap");
var isoToday = /* @__PURE__ */ __name((t) => new Intl.DateTimeFormat("en-CA", { timeZone: "America/Fortaleza", year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date(t)), "isoToday");
var own = /* @__PURE__ */ __name((s, c) => s.role === "CONTROLADORIA" || s.role === "SUPERVISOR" && c.supervisor === s.user, "own");
function buildOperations(db, next, session, timestamp = (/* @__PURE__ */ new Date()).toISOString()) {
  if (session.role === "VISUALIZAR") fail("Este perfil permite somente visualiza\xE7\xE3o.", 403);
  const base = visibleState(db, session), ops = [], releaseUses = /* @__PURE__ */ new Map();
  const add = /* @__PURE__ */ __name((table, action, id2, data) => ops.push({ table, action, id: String(id2), ...data ? { data } : {} }), "add");
  const correctService = /* @__PURE__ */ __name((service, convocationId, reason) => {
    const old = {
      id: String(service.id),
      convocacaoId: String(service.convocacao_id),
      obraId: String(service.obra_id || ""),
      obraNome: service.obra_nome_snapshot || "",
      unidade: service.unidade_snapshot || "",
      periodo: service.periodo || "",
      principal: Boolean(service.principal),
      criadoEm: service.criado_em || null
    };
    add("auditoria", "insert", "audit:" + crypto.randomUUID(), {
      entidade: "servicos_apontamento",
      entidade_id: String(service.id),
      acao: "CORRECAO_VINCULO_SERVICO_APONTAMENTO",
      usuario: session.user,
      ocorrido_em: timestamp,
      antes: old,
      depois: { vinculoAtivo: false },
      contexto: { servicoId: String(service.id), convocacaoId: String(convocationId), motivo: reason }
    });
    add("servicos_apontamento", "delete", String(service.id));
  }, "correctService");
  for (const key2 of ["colaboradores", "obras", "convocacoes", "apontamentos", "indisponibilidades", "conflitosTentados"]) if (!Array.isArray(next[key2])) fail("Dados incompletos. Atualize a p\xE1gina.");
  const staff = new Map(next.colaboradores.map((p2) => [String(p2.id), p2])), oldStaff = new Map(base.colaboradores.map((p2) => [p2.id, p2])), works = new Map(next.obras.map((o) => [String(o.id), o]));
  if (staff.size !== next.colaboradores.length || works.size !== next.obras.length) fail("H\xE1 identificadores repetidos.");
  const nomesCadastrados = /* @__PURE__ */ new Map();
  const isEventAvulso = /* @__PURE__ */ __name((p2) => p2?.avulsoRegistro === true || p2?.avulso === "Sim" && !oldStaff.has(String(p2.id)) && !numericId(String(p2.id)), "isEventAvulso");
  for (const p2 of next.colaboradores) {
    if (isEventAvulso(p2)) continue;
    const nome = String(p2.nome || "").trim().toUpperCase();
    if (!nome) continue;
    const outro = nomesCadastrados.get(nome);
    if (outro && outro !== String(p2.id))
      fail("O colaborador " + p2.nome + " j\xE1 possui cadastro. Selecione o cadastro existente no retroativo; n\xE3o crie outro avulso. Nenhum registro foi alterado.", 409);
    nomesCadastrados.set(nome, String(p2.id));
  }
  const staffFields = ["nome", "funcao", "custo", "moradia", "inativo", "categoria", "avulso"];
  for (const p2 of next.colaboradores) {
    const old = oldStaff.get(String(p2.id));
    if (isEventAvulso(p2)) {
      if (old && !same(field(old, staffFields), field(p2, staffFields)))
        fail("Os dados de um avulso hist\xF3rico n\xE3o podem ser alterados pelo cadastro.", 403);
      if (!old && (!String(p2.nome || "").trim() || !String(p2.funcao || "").trim() || !finite(p2.custo) || Number(p2.custo) <= 0 || numericId(String(p2.id))))
        fail("Avulso manual inv\xE1lido.", 400);
      continue;
    }
    if (old && same(field(old, staffFields), field(p2, staffFields))) continue;
    if (session.role !== "CONTROLADORIA" && (old || session.role !== "SUPERVISOR" || p2.avulso !== "Sim")) fail("Sem permiss\xE3o para alterar colaboradores.", 403);
    if (!old && numericId(p2.id)) fail("Cadastro novo com identificador inv\xE1lido.");
    if (!finite(p2.custo) || Number(p2.custo) <= 0) fail("Custo di\xE1rio inv\xE1lido.");
    add("colaboradores", old ? "update" : "insert", p2.id, { nome: required(p2.nome, "Nome"), funcao: required(p2.funcao, "Fun\xE7\xE3o"), valor_diaria: money(p2.custo), local_moradia: String(p2.moradia || ""), ativo: !p2.inativo, categoria_diaria: String(p2.categoria || ""), avulso: p2.avulso === "Sim" ? "Sim" : "N\xE3o" });
  }
  for (const person of staff.values()) if (isEventAvulso(person) && !oldStaff.has(String(person.id)) && !next.convocacoes.some((c) => c.colaboradores.some((id2) => String(id2) === String(person.id))))
    fail("Avulso s\xF3 pode ser inclu\xEDdo manualmente em Convoca\xE7\xE3o ou Apontamento, sem cadastro.", 403);
  if ([...oldStaff.keys()].some((k) => !staff.has(k))) fail("Use a inativa\xE7\xE3o para preservar o hist\xF3rico do colaborador.");
  const oldWorks = new Map(base.obras.map((o) => [o.id, o]));
  for (const o of next.obras) {
    const old = oldWorks.get(String(o.id));
    if (old && same(field(old, ["nome", "unidade"]), field(o, ["nome", "unidade"]))) continue;
    if (session.role !== "CONTROLADORIA") fail("Sem permiss\xE3o para alterar obras.", 403);
    if (!old && numericId(o.id)) fail("Obra nova com identificador inv\xE1lido.");
    add("obras", old ? "update" : "insert", o.id, { nome: required(o.nome, "Obra"), unidade: required(o.unidade, "Unidade") });
  }
  for (const o of base.obras) if (!works.has(o.id)) {
    if (session.role !== "CONTROLADORIA") fail("Sem permiss\xE3o para excluir obra.", 403);
    if (db.raw.convocacoes.some((c) => String(c.obra_id) === o.id) || db.raw.servicos_apontamento.some((x2) => String(x2.obra_id) === o.id) || next.convocacoes.some((c) => String(c.obraId) === o.id) || next.apontamentos.some((a2) => a2.itens.some((i) => normServices(i).some((s) => s.obraId === o.id)))) fail("Esta obra possui convoca\xE7\xF5es ou apontamentos vinculados e deve ser preservada.");
    add("obras", "delete", o.id);
  }
  const oldConvs = new Map(base.convocacoes.map((c) => [c.id, c])), rawConvs = new Map(db.raw.convocacoes.map((c) => [String(c.id), c]));
  const records = /* @__PURE__ */ new Map(), byGroup = /* @__PURE__ */ new Map(), rawAps = new Map(db.raw.apontamentos.map((a2) => [String(a2.convocacao_id), a2])), oldApByConv = new Map(base.apontamentos.map((a2) => [String(a2.convocacaoId), a2]));
  const rawServicesByConv = /* @__PURE__ */ new Map();
  for (const service of db.raw.servicos_apontamento) {
    const id2 = String(service.convocacao_id);
    if (!rawServicesByConv.has(id2)) rawServicesByConv.set(id2, []);
    rawServicesByConv.get(id2).push(service);
  }
  for (const c of next.convocacoes) {
    const old = oldConvs.get(String(c.id));
    date(c.dataServico);
    period(c.turno);
    if (!supervisors.includes(c.supervisor) && !(session.role === "CONTROLADORIA" && c.supervisor === "PAULO") && (!old || c.supervisor !== old.supervisor)) fail("Supervisor inv\xE1lido.");
    if (!Array.isArray(c.colaboradores) || !c.colaboradores.length || new Set(c.colaboradores).size !== c.colaboradores.length) fail("Equipe vazia ou duplicada.");
    if (!old && numericId(c.id)) fail("Convoca\xE7\xE3o nova com identificador inv\xE1lido.");
    for (const pidValue of c.colaboradores) {
      const pid = String(pidValue), person = staff.get(pid);
      if (!person) fail("Colaborador n\xE3o encontrado.");
      const key2 = old?.colaboradores.includes(pid) ? old.id : `cv:${c.id}:${pid}`, scheduling = field(c, ["supervisor", "dataServico", "unidade", "turno"]), changed = !old || !old.colaboradores.includes(pid) || !same(scheduling, field(old, ["supervisor", "dataServico", "unidade", "turno"]));
      if (changed && !own(session, c)) fail("Voc\xEA s\xF3 pode convocar sua pr\xF3pria equipe.", 403);
      if (changed && old && !own(session, old)) fail("Voc\xEA n\xE3o pode alterar a equipe de outro supervisor.", 403);
      if (changed && session.role === "SUPERVISOR" && person.inativo) fail("Colaborador inativo.");
      if (records.has(key2)) fail("Convoca\xE7\xE3o repetida.");
      records.set(key2, { key: key2, c, pid, old: old?.colaboradores.includes(pid) ? old : null, changed });
      byGroup.set(String(c.id) + "|" + pid, key2);
    }
  }
  const pointed = /* @__PURE__ */ new Map();
  for (const a2 of next.apontamentos) {
    if (!Array.isArray(a2.itens) || !a2.itens.length) fail("Apontamento vazio.");
    for (const i of a2.itens) {
      const key2 = byGroup.get(String(a2.convocacaoId) + "|" + String(i.colaboradorId));
      if (!key2) fail("Apontamento sem convoca\xE7\xE3o correspondente.");
      if (pointed.has(key2)) fail("Apontamento duplicado.");
      pointed.set(key2, { a: a2, i });
    }
  }
  for (const record of records.values()) {
    const { key: key2, c, pid, changed } = record;
    if (!changed) continue;
    if (isEventAvulso(staff.get(pid)) && records.values().some((other) => other.key !== key2 && other.c.dataServico === c.dataServico && overlap(other.c.turno, c.turno) && clean(staff.get(other.pid)?.nome || "") === clean(staff.get(pid).nome)))
      fail("Este avulso j\xE1 foi inclu\xEDdo no mesmo dia e turno. Confira o apontamento existente.", 409);
    for (const other of records.values()) if (other.key !== key2 && other.pid === pid && other.c.dataServico === c.dataServico && overlap(other.c.turno, c.turno)) fail(`Conflito: ${staff.get(pid).nome} j\xE1 est\xE1 convocado por ${other.c.supervisor}, em ${other.c.unidade}, no turno ${other.c.turno}.`, 409, { colaboradorId: pid, supervisor: other.c.supervisor, unidade: other.c.unidade, turno: other.c.turno });
    const blocked = db.state.indisponibilidades.find((x2) => x2.colaboradorId === pid && x2.inicio <= c.dataServico && x2.fim >= c.dataServico);
    if (blocked && present(pointed.get(key2)?.i.status || "Presente (Integral)")) fail(`${staff.get(pid).nome} est\xE1 indispon\xEDvel: ${blocked.motivo}.`, 409);
  }
  for (const old of base.convocacoes) {
    if (records.has(old.id)) continue;
    if (session.role === "SUPERVISOR") continue;
    if (!own(session, old)) fail("Sem permiss\xE3o para excluir esta convoca\xE7\xE3o.", 403);
    for (const s of rawServicesByConv.get(old.id) || []) add("servicos_apontamento", "delete", s.id);
    const ap = rawAps.get(old.id);
    if (ap) add("apontamentos", "delete", ap.id);
    add("convocacoes", "delete", old.id);
  }
  for (const { key: key2, c, pid, old, changed } of records.values()) {
    const person = staff.get(pid);
    const raw = old ? rawConvs.get(old.id) : null, oldPoint = oldApByConv.get(String(old?.id))?.itens.find((i2) => i2.colaboradorId === pid), ap = pointed.get(key2), pointChanged = ap && (changed || !same(apView(oldPoint), apView(ap.i)));
    if (oldPoint && !ap) {
      if (session.role === "SUPERVISOR") continue;
      if (!own(session, c)) fail("Sem permiss\xE3o para remover apontamento.", 403);
      const row = rawAps.get(key2);
      if (row) add("apontamentos", "delete", row.id);
      for (const s of rawServicesByConv.get(key2) || []) add("servicos_apontamento", "delete", s.id);
      const { text, meta: meta2 } = metadata(raw.observacao);
      delete meta2.apontado_em;
      delete meta2.apontado_por;
      delete meta2.apontamento_atrasado;
      delete meta2.valor_ajuda_custo;
      add("convocacoes", "update", key2, { status: "Presente (Integral)", valor_extra: 0, custo_pago: 0, valor_acordo: 0, valor_adicional_noturno: 0, custos_separados: false, observacao: text + (Object.keys(meta2).length ? " ||APROAR_META|| " + JSON.stringify(meta2) : "") });
    }
    const financeLocked = session.role === "SUPERVISOR" && oldPoint?.financeAdjusted && afterFinancialDeadline(c.dataServico, timestamp);
    if (pointChanged) {
      if (session.role === "SUPERVISOR") {
        const fields2 = changedFinancialFields(oldPoint, ap.i);
        ops.push(...requireApprovedReleases(db.releaseEvents, { supervisor: session.user, colaboradorId: pid, dataServico: c.dataServico, fields: fields2 }, timestamp, releaseUses));
      }
      if (session.role === "FINANCEIRO") {
        if (!oldPoint) fail("Financeiro n\xE3o cria apontamentos.", 403);
        const ignore = /* @__PURE__ */ __name((i2) => {
          const x2 = apView(i2);
          delete x2.financeiro;
          delete x2.noturno;
          delete x2.acordo;
          delete x2.ajudaCusto;
          return x2;
        }, "ignore");
        if (!same(ignore(oldPoint), ignore(ap.i))) fail("Financeiro s\xF3 altera pagamentos, adicionais, acordos e passagens/ajuda de custo.", 403);
      } else if (!own(session, c)) fail("Voc\xEA s\xF3 pode apontar sua pr\xF3pria equipe.", 403);
      if (c.dataServico > isoToday(timestamp)) fail("Apontamento n\xE3o aceita data futura.");
      if (!["Presente (Integral)", "Presente (S\xF3 Manh\xE3)", "Presente (S\xF3 Tarde)", "Sa\xEDda Antecipada", "Falta", "Atestado"].includes(ap.i.status)) fail("Status inv\xE1lido.");
      if (!["Valor espec\xEDfico", ...Object.keys({ "N\xE3o": 0, "Meia di\xE1ria": 0.5, "Di\xE1ria": 1, "Uma e meia di\xE1ria": 1.5, "Duas di\xE1rias": 2 })].includes(ap.i.extra)) fail("Extra inv\xE1lido.");
      for (const k of ["financeiro", "noturno", "acordo", "ajudaCusto"]) if (!finite(ap.i[k] ?? 0)) fail("Valor financeiro inv\xE1lido.");
      if (!finite(ap.i.valorExtraDisponivel ?? 0)) fail("Valor da extra dispon\xEDvel inv\xE1lido.");
      if (oldPoint && Number(ap.i.ajudaCusto ?? 0) !== Number(oldPoint.ajudaCusto ?? 0) && session.role !== "FINANCEIRO" && (session.role !== "SUPERVISOR" || financeLocked)) fail("Somente o Financeiro pode alterar passagens/ajuda de custo ap\xF3s o ajuste financeiro.", 403);
      const ss2 = normServices(ap.i);
      if (present(ap.i.status) && (!ss2.length || ss2.some((s) => !works.has(s.obraId)))) fail("Defina servi\xE7os cadastrados para o colaborador. Os servi\xE7os podem pertencer a qualquer unidade.");
      for (const [index, s] of ss2.entries()) {
        if (!s.obraId) continue;
        period(s.periodo);
        if (index === 0 && (s.extra !== "Não" || s.extraIndependente)) fail("O serviço principal usa o campo de extra existente na ficha.");
        if (!["Não", "Meia diária", "Diária", "Uma e meia diária", "Duas diárias"].includes(s.extra)) fail("Extra do serviço adicional inválida.");
        if (s.extraIndependente && s.extra === "Não") fail("Serviço independente sem extra selecionada.");
        if (!present(ap.i.status) && s.extra !== "Não") fail("Não é permitido extra por serviço em apontamento de falta ou atestado.");
      }
      if (new Set(ss2.map((s) => s.obraId + "|" + s.periodo)).size !== ss2.length) fail("Servi\xE7o repetido no mesmo per\xEDodo.");
      if (ap.i.extra === "Valor espec\xEDfico" && (!oldPoint || oldPoint.extra !== "Valor espec\xEDfico")) fail("Extra espec\xEDfico deve existir no registro original.");
    }
    const work = c.obraId && works.has(String(c.obraId)) ? String(c.obraId) : [...works.values()].find((o) => o.unidade === c.unidade)?.id;
    if (!work) fail("Cadastre ao menos uma obra para esta unidade.");
    if (!raw || changed || String(old?.obraId || "") !== String(c.obraId || "")) {
      if (raw && !own(session, c) && session.role !== "FINANCEIRO") fail("Sem permiss\xE3o para alterar convoca\xE7\xE3o.", 403);
      if (raw && session.role === "FINANCEIRO") fail("Financeiro n\xE3o altera convoca\xE7\xF5es.", 403);
      const { meta: meta2 } = metadata(raw?.observacao), created = raw?.criado_em || meta2.convocado_em || timestamp;
      Object.assign(meta2, { convocado_em: created, convocado_por: raw?.criado_por || meta2.convocado_por || session.user, servico_a_definir: !c.obraId, unidade_convocada: meta2.unidade_convocada || c.unidade });
      if (isEventAvulso(person)) {
        Object.assign(meta2, { avulso_eventual: {
          id: pid,
          nome: String(person.nome).trim(),
          funcao: person.funcao,
          custo: money(person.custo),
          categoria: person.categoria || "",
          criado_em: created
        } });
      }
      const data = { obra_id: work, colaborador_id: isEventAvulso(person) ? null : pid, data: c.dataServico, engenheiro: c.supervisor, turno: c.turno, observacao: "Turno: " + c.turno + " ||APROAR_META|| " + JSON.stringify(meta2) };
      if (!raw) Object.assign(data, { status: "Presente (Integral)", valor_extra: 0, criado_em: timestamp, criado_por: session.user });
      add("convocacoes", raw ? "update" : "insert", key2, data);
    }
    if (!pointChanged) continue;
    const authorizedFields = new Set([...releaseUses.values()].filter(
      (x2) => x2.supervisor === session.user && x2.colaboradorId === String(pid) && x2.dataServico === c.dataServico
    ).flatMap((x2) => x2.fields));
    if (financeLocked && money(Number(ap.i.noturno ?? 0)) !== money(Number(oldPoint.noturno ?? 0)) && !authorizedFields.has("Adicional noturno"))
      fail("O adicional noturno foi ajustado pelo Financeiro. O valor selecionado N\xC3O foi salvo; solicite autoriza\xE7\xE3o da Controladoria ou do Financeiro para alter\xE1-lo.", 403);
    const i = { ...ap.i };
    if (pendingAvulsoInvalid(i, staff.get(pid))) fail("Escolha um tipo v\xE1lido de di\xE1ria para o avulso.");
    if (session.role === "SUPERVISOR" && oldPoint?.financeAdjusted) {
      const authorized = [...authorizedFields];
      if (!authorized.includes("Complemento financeiro")) i.financeiro = oldPoint.financeiro;
      if (financeLocked) {
        const labels = { noturno: "Adicional noturno", acordo: "Bonifica\xE7\xE3o", ajudaCusto: "Passagem / ajuda de custo" };
        for (const k of ["noturno", "acordo", "ajudaCusto"]) if (!authorized.includes(labels[k])) i[k] = oldPoint[k];
      }
    }
    const p2 = staff.get(pid), isPresent = present(i.status), ss = normServices(i).filter((s) => s.obraId), hasSebrae = ss.some((s) => clean(works.get(s.obraId)?.unidade) === "SEBRAE"), financialAdjusted = session.role === "FINANCEIRO" || oldPoint?.financeAdjusted === true;
    const extra = isPresent ? i.extra === "Valor espec\xEDfico" ? Number(oldPoint.valorExtraOriginal) : money(Number(p2.custo) * mult(i.extra)) : 0;
    const night = isPresent ? hasSebrae ? Number(i.noturno ?? 0) : Number(oldPoint?.noturno || 0) : 0, finance = isPresent ? Number(i.financeiro) : 0, bonus = isPresent ? Number(i.acordo) : 0, ajudaCusto = isPresent ? Number(i.ajudaCusto || 0) : 0;
    const approvedMeta = metadata(raw?.observacao).meta;
    if (finance > 0 && bonus > 0 && money(finance) === money(bonus) && !hasValidComplementApproval(approvedMeta, finance, bonus))
      fail("O valor complementar repete o acordo/bonifica\xE7\xE3o. N\xE3o grave duas vezes o mesmo pagamento: deixe apenas o acordo ou solicite confirma\xE7\xE3o ao Financeiro.");
    const weight = !isPresent ? 0 : p2.avulso === "Sim" && avulsoDailyTypes.includes(i.tipoDiariaAvulso) ? mult(i.tipoDiariaAvulso) : ["Presente (S\xF3 Manh\xE3)", "Presente (S\xF3 Tarde)", "Sa\xEDda Antecipada"].includes(i.status) ? 0.5 : ["Manh\xE3", "Tarde"].includes(c.turno) ? 0.5 : 1;
    const oldRow = rawAps.get(key2), pointTime = oldRow?.apontado_em || metadata(raw?.observacao).meta.apontado_em || timestamp, executor = oldRow?.apontado_por || metadata(raw?.observacao).meta.apontado_por || session.user;
    const values = { status: i.status, valor_extra: extra, observacao: String(i.observacao || ""), tipo_diaria: i.extra === "Valor espec\xEDfico" ? oldPoint?.tipoDiariaOriginal || "N\xE3o" : i.extra, custo_pago: money(finance), custo_pago_definido_financeiro: financialAdjusted, valor_acordo: money(bonus), valor_adicional_noturno: money(night), custo_encargos_base: money(Number(p2.custo) * weight + extra), custos_separados: true, migracao_sebrae_noturno_v2: true };
    add("apontamentos", oldRow ? "update" : "insert", oldRow?.id || "ap:" + key2, { ...values, convocacao_id: key2, data_servico: c.dataServico, colaborador_id: pid, engenheiro: c.supervisor, apontado_em: pointTime, apontado_por: executor, retroativo: Boolean(oldRow?.retroativo || ap.a.retroativo), atualizado_em: timestamp });
    ops.push(...financialHistoryEvents({
      convocationId: key2,
      colaboradorId: pid,
      dataServico: c.dataServico,
      supervisor: c.supervisor,
      actor: session.user,
      role: session.role,
      source: "Apontamento",
      timestamp,
      previous: oldRow,
      next: values
    }));
    const oldMeta = clearObsoleteApproval(metadata(raw?.observacao).meta, finance, bonus);
    const eventSnapshot = isEventAvulso(p2) ? { avulso_eventual: {
      id: pid,
      nome: String(p2.nome).trim(),
      funcao: p2.funcao,
      custo: money(p2.custo),
      categoria: p2.categoria || "",
      criado_em: oldMeta.avulso_eventual?.criado_em || timestamp
    } } : {};
    const first = ss[0], meta = { ...oldMeta, ...eventSnapshot, unidade_convocada: oldMeta.unidade_convocada || c.unidade, valor_extra_disponivel: money(Number(i.valorExtraDisponivel ?? 0)), apontado_em: pointTime, apontado_por: executor, custos_separados: true, custo_pago: money(finance), valor_acordo: money(bonus), valor_adicional_noturno: money(night), valor_ajuda_custo: money(ajudaCusto), servico_a_definir: !first, tipo_diaria_avulso: p2.avulso === "Sim" ? i.tipoDiariaAvulso || "Di\xE1ria" : null, periodo_principal: first?.periodo || c.turno, servicos_adicionais: ss.slice(1).map((s) => ({ servico: works.get(s.obraId)?.nome, obra_id: s.obraId, periodo: s.periodo, extra: s.extra, extra_independente: s.extraIndependente })) };
    add("convocacoes", "update", key2, { ...values, obra_id: first?.obraId || work, observacao: "Turno: " + c.turno + (i.observacao ? " | Obs: " + i.observacao : "") + " ||APROAR_META|| " + JSON.stringify(meta) });
    // Conferir tanto o que o apontamento apresenta quanto os vínculos reais:
    // metadados legados podem parecer iguais enquanto falta uma linha no Neon.
    const previousServices = (rawServicesByConv.get(key2) || []).slice().sort((a2, b2) => Number(b2.principal) - Number(a2.principal) || Number(a2.id) - Number(b2.id));
    const samePersistedServices=previousServices.length===ss.length&&previousServices.every((row,index)=>
      String(row.obra_id||"")===String(ss[index].obraId||"")&&
      String(row.periodo||"Integral")===String(ss[index].periodo||"Integral")&&
      Boolean(row.principal)===(index===0));
    if (!same(normServices(oldPoint), ss) || !samePersistedServices) {
      ss.forEach((service, index) => {
        const work2 = works.get(service.obraId), previous = previousServices[index];
        const values2 = { convocacao_id: key2, obra_id: service.obraId, obra_nome_snapshot: work2.nome, unidade_snapshot: work2.unidade, periodo: service.periodo, principal: index === 0, atualizado_em: timestamp };
        if (previous) add("servicos_apontamento", "update", String(previous.id), values2);
        else add("servicos_apontamento", "insert", `service:${key2}:${index}`, { ...values2, criado_em: timestamp });
      });
      for (const previous of previousServices.slice(ss.length))
        correctService(previous, key2, "Corre\xE7\xE3o da lista de servi\xE7os no apontamento");
    }
  }
  if (Array.isArray(next.extras)) {
    const oldExtras = new Map((base.extras || []).map((x2) => [String(x2.id), x2]));
    const allExtras = db.state.extras || [], incomingIds = /* @__PURE__ */ new Set(), incomingCombos = /* @__PURE__ */ new Set();
    const rawExtraConvs = new Map(db.raw.convocacoes.filter((c) => metadata(c.observacao).meta.extra_avulsa === true).map((c) => [String(c.id), c]));
    for (const x2 of next.extras) {
      const id2 = String(x2.id || "");
      if (!id2) fail("Identificador do extra inv\xE1lido.");
      if (incomingIds.has(id2)) fail("Extra duplicada.");
      incomingIds.add(id2);
      const old = oldExtras.get(id2);
      if (!old && numericId(id2)) fail("Identificador novo de extra inv\xE1lido.");
      if (session.role !== "SUPERVISOR" && session.role !== "CONTROLADORIA") fail("Sem permiss\xE3o para lan\xE7ar extras.", 403);
      if (old && !own(session, { supervisor: old.supervisor })) fail("Voc\xEA n\xE3o pode alterar a extra de outro supervisor.", 403);
      if (x2.cancelada === true) {
        if (!old) fail("Extra inexistente. Atualize os dados e tente novamente.", 409);
        const reason = String(x2.motivoCancelamento || "").trim();
        if (reason.length < 10 || reason.length > 600) fail("Informe o motivo do cancelamento da extra (10 a 600 caracteres).");
        const previousConv = rawExtraConvs.get(id2), previousPoint = rawAps.get(id2);
        if (!previousConv || !previousPoint) fail("Registro hist\xF3rico da extra incompleto. Solicite confer\xEAncia \xE0 Controladoria.", 409);
        if (session.role === "SUPERVISOR") {
          ops.push(...requireApprovedReleases(db.releaseEvents, { supervisor: session.user, colaboradorId: old.colaboradorId, dataServico: old.dataServico, fields: ["Extra"] }, timestamp, releaseUses));
        }
        const { text, meta: meta2 } = metadata(previousConv.observacao);
        const updatedMeta = {
          ...meta2,
          extra_cancelada: true,
          extra_cancelada_em: timestamp,
          extra_cancelada_por: session.user,
          extra_cancelada_motivo: reason,
          extra_valor_original: money(Number(previousPoint.valor_extra ?? old.valorExtraOriginal))
        };
        add("convocacoes", "update", id2, { valor_extra: 0, custo_encargos_base: 0, observacao: text + " ||APROAR_META|| " + JSON.stringify(updatedMeta) });
        add("apontamentos", "update", String(previousPoint.id), { valor_extra: 0, custo_encargos_base: 0, atualizado_em: timestamp });
        ops.push(...financialHistoryEvents({
          convocationId: id2,
          colaboradorId: old.colaboradorId,
          dataServico: old.dataServico,
          supervisor: old.supervisor,
          actor: session.user,
          role: session.role,
          source: "Cancelamento de extra indevida",
          timestamp,
          previous: previousPoint,
          next: { ...previousPoint, valor_extra: 0 }
        }));
        add("auditoria", "insert", "audit:" + crypto.randomUUID(), {
          entidade: "apontamentos",
          entidade_id: String(id2),
          acao: "CANCELAMENTO_EXTRA_INDEVIDA",
          usuario: session.user,
          ocorrido_em: timestamp,
          contexto: {
            convocacaoId: id2,
            colaboradorId: String(old.colaboradorId),
            dataServico: old.dataServico,
            valorAnterior: money(Number(previousPoint.valor_extra ?? old.valorExtraOriginal)),
            valorNovo: 0,
            motivo: reason
          }
        });
        continue;
      }
      const personId = String(x2.colaboradorId || ""), p2 = staff.get(personId), work = works.get(String(x2.obraId || ""));
      if (!p2) fail("Colaborador n\xE3o encontrado para a extra.");
      const serviceDate = date(x2.dataServico);
      if (serviceDate > isoToday(timestamp)) fail("Extra n\xE3o aceita data futura.");
      if (!work) fail("Escolha um servi\xE7o v\xE1lido para a extra.");
      const supervisor = session.role === "SUPERVISOR" ? session.user : required(String(x2.supervisor || old?.supervisor || ""), "Supervisor respons\xE1vel");
      if (!supervisors.includes(supervisor)) fail("Supervisor inv\xE1lido para a extra.");
      const kind = String(x2.extra || ""), factor = mult(kind);
      if (!factor) fail("Selecione um tipo de extra v\xE1lido.");
      const combo = serviceDate + "|" + personId + "|" + String(work.id);
      if (incomingCombos.has(combo)) fail("H\xE1 duas extras para o mesmo colaborador, data e servi\xE7o.");
      incomingCombos.add(combo);
      const duplicate = allExtras.find((y2) => String(y2.id) !== id2 && y2.dataServico === serviceDate && String(y2.colaboradorId) === personId && String(y2.obraId) === String(work.id));
      if (duplicate) fail("J\xE1 existe uma extra para este colaborador, data e servi\xE7o.", 409, { extraId: duplicate.id });
      const raw = old ? rawExtraConvs.get(id2) : null, rawPoint = old ? rawAps.get(id2) : null;
      const oldMeta = metadata(raw?.observacao).meta, obs = String(x2.observacao || "").trim().slice(0, 2e3);
      const dayConv = (db.state.convocacoes || []).find((c) => c.dataServico === serviceDate && c.colaboradores?.includes(personId));
      const dayWorkId = String(dayConv?.obraId || old?.servicoDiaId || "");
      const amount2 = money(Number(x2.valorExtraOriginal));
      const unchanged = old && old.supervisor === supervisor && old.dataServico === serviceDate && String(old.colaboradorId) === personId && String(old.obraId) === String(work.id) && old.extra === kind && String(old.observacao || "") === obs && money(Number(old.valorExtraOriginal) || 0) === amount2;
      if (unchanged) continue;
      if (session.role === "SUPERVISOR") {
        ops.push(...requireApprovedReleases(db.releaseEvents, { supervisor: session.user, colaboradorId: personId, dataServico: serviceDate, fields: ["Extra"] }, timestamp, releaseUses));
      }
      if (!finite(x2.valorExtraOriginal) || amount2 <= 0) fail("Informe o Valor da Extra em reais; o valor n\xE3o \xE9 pr\xE9-definido.");
      const created = old?.criadoEm || oldMeta.extra_lancado_em || timestamp, creator = old?.executor || oldMeta.extra_lancado_por || session.user;
      const meta = { ...oldMeta, extra_avulsa: true, extra_obra_id: String(work.id), extra_unidade: work.unidade, extra_dia_obra_id: dayWorkId, extra_observacao: obs, extra_lancado_em: created, extra_lancado_por: creator, apontado_em: created, apontado_por: creator, custos_separados: true, servico_a_definir: false };
      const convData = { obra_id: String(work.id), colaborador_id: personId, data: serviceDate, engenheiro: supervisor, turno: "Integral", status: "Extra", valor_extra: amount2, custo_pago: 0, valor_acordo: 0, valor_adicional_noturno: 0, custo_encargos_base: amount2, custos_separados: true, observacao: "Extra independente ||APROAR_META|| " + JSON.stringify(meta) };
      const convKey = old ? id2 : "extra:" + id2;
      if (old) add("convocacoes", "update", id2, convData);
      else add("convocacoes", "insert", convKey, { ...convData, criado_em: timestamp, criado_por: session.user });
      const pointData = { convocacao_id: convKey, data_servico: serviceDate, colaborador_id: personId, engenheiro: supervisor, status: "Extra", valor_extra: amount2, observacao: obs, tipo_diaria: kind, custo_pago: 0, custo_pago_definido_financeiro: false, valor_acordo: 0, valor_adicional_noturno: 0, custo_encargos_base: amount2, custos_separados: true, migracao_sebrae_noturno_v2: true, apontado_em: created, apontado_por: creator, retroativo: serviceDate < isoToday(timestamp), atualizado_em: timestamp };
      add("apontamentos", rawPoint ? "update" : "insert", rawPoint?.id || "extra-ap:" + id2, pointData);
      ops.push(...financialHistoryEvents({
        convocationId: convKey,
        colaboradorId: personId,
        dataServico: serviceDate,
        supervisor,
        actor: session.user,
        role: session.role,
        source: "Extra independente",
        timestamp,
        previous: rawPoint,
        next: pointData
      }));
      if (!old || String(old.obraId) !== String(work.id) || (rawServicesByConv.get(id2) || []).length === 0) {
        if (old) for (const service of rawServicesByConv.get(id2) || []) correctService(service, id2, "Realoca\xE7\xE3o da obra de extra independente");
        add("servicos_apontamento", "insert", "extra-service:" + id2, { convocacao_id: convKey, obra_id: String(work.id), obra_nome_snapshot: work.nome, unidade_snapshot: work.unidade, periodo: "Integral", principal: true, criado_em: timestamp, atualizado_em: timestamp });
      }
    }
    for (const old of base.extras || []) {
      if (incomingIds.has(String(old.id))) continue;
      if (session.role === "SUPERVISOR") continue;
      if (!own(session, { supervisor: old.supervisor })) fail("Sem permiss\xE3o para excluir esta extra.", 403);
      if (session.role === "SUPERVISOR") {
        ops.push(...requireApprovedReleases(db.releaseEvents, { supervisor: session.user, colaboradorId: old.colaboradorId, dataServico: old.dataServico, fields: ["Extra"] }, timestamp, releaseUses));
      }
      for (const service of rawServicesByConv.get(String(old.id)) || []) add("servicos_apontamento", "delete", service.id);
      const row = rawAps.get(String(old.id));
      if (row) add("apontamentos", "delete", row.id);
      add("convocacoes", "delete", old.id);
    }
  }
  const sync = /* @__PURE__ */ __name((name, table, convert, allowed) => {
    const old = new Map(base[name].map((x2) => [String(x2.id), x2]));
    for (const x2 of next[name]) {
      const previous = old.get(String(x2.id));
      if (previous && same(previous, x2)) continue;
      if (!allowed(x2, previous)) fail("Sem permiss\xE3o para alterar " + name + ".", 403);
      if (!previous && numericId(x2.id)) fail("Identificador novo inv\xE1lido.");
      add(table, previous ? "update" : "insert", x2.id, convert(x2, previous));
    }
    for (const x2 of base[name]) if (!next[name].some((y2) => String(y2.id) === String(x2.id))) {
      if (session.role !== "CONTROLADORIA") fail("Sem permiss\xE3o para excluir registro.", 403);
      add(table, "delete", x2.id);
    }
  }, "sync");
  sync("indisponibilidades", "indisponibilidades", (x2) => {
    if (!staff.has(String(x2.colaboradorId))) fail("Colaborador inv\xE1lido.");
    date(x2.inicio);
    date(x2.fim);
    if (x2.fim < x2.inicio) fail("Per\xEDodo inv\xE1lido.");
    return { colaborador_id: String(x2.colaboradorId), colaborador_nome_snapshot: staff.get(String(x2.colaboradorId)).nome, motivo: required(x2.motivo, "Motivo"), inicio: x2.inicio, fim: x2.fim, observacao: String(x2.obs || x2.observacao || ""), criado_por: session.user, ativo: true };
  }, () => session.role === "CONTROLADORIA");
  sync("conflitosTentados", "conflitos_convocacao", (x2, previous) => previous ? { resolvido: Boolean(x2.resolvido), resolvido_em: x2.resolvido ? timestamp : null, resolvido_por: x2.resolvido ? session.user : null } : { colaborador_id: String(x2.colaboradorId), colaborador_nome_snapshot: staff.get(String(x2.colaboradorId))?.nome || "", data: date(x2.dataServico), convocacao_existente_id: String(x2.convocacaoExistenteId || ""), engenheiro_original: required(x2.supervisorExistente, "Supervisor original"), turno_original: period(x2.turnoExistente), unidade_original: String(x2.unidadeExistente || ""), engenheiro_tentativa: session.role === "SUPERVISOR" ? session.user : required(x2.supervisor, "Supervisor"), turno_tentativa: period(x2.turno), unidade_tentativa: String(x2.unidade || ""), criado_em: timestamp, resolvido: false, contexto: { origem: "aproar-web" } }, (x2, previous) => previous ? session.role === "CONTROLADORIA" : ["CONTROLADORIA", "SUPERVISOR"].includes(session.role));
  const baseNoConv = base.semConvocacoesUnidade || [], incomingNoConv = next.semConvocacoesUnidade ?? baseNoConv;
  if (!Array.isArray(incomingNoConv) || incomingNoConv.length > 3e4) fail("Confirma\xE7\xF5es sem convoca\xE7\xE3o inv\xE1lidas.");
  const noConvKey = /* @__PURE__ */ __name((x2) => String(x2.supervisor) + "|" + String(x2.unidade) + "|" + String(x2.dataServico), "noConvKey");
  const oldNoConv = new Map(baseNoConv.map((x2) => [noConvKey(x2), x2]));
  if (oldNoConv.size !== baseNoConv.length) fail("H\xE1 confirma\xE7\xF5es hist\xF3ricas duplicadas.");
  const savedNoConv = [], incomingKeys = /* @__PURE__ */ new Set();
  for (const x2 of incomingNoConv) {
    if (!x2 || typeof x2 !== "object" || Array.isArray(x2)) fail("Confirma\xE7\xE3o sem convoca\xE7\xE3o inv\xE1lida.");
    const key2 = noConvKey(x2), old = oldNoConv.get(key2);
    if (incomingKeys.has(key2)) fail("Confirma\xE7\xE3o sem convoca\xE7\xE3o duplicada.");
    incomingKeys.add(key2);
    if (old && same(old, x2)) {
      if (next.convocacoes.some((c) => c.supervisor === x2.supervisor && c.unidade === x2.unidade && c.dataServico === x2.dataServico)) fail("J\xE1 existe convoca\xE7\xE3o nesta unidade e data. Desfa\xE7a a confirma\xE7\xE3o antes de convocar.");
      savedNoConv.push(old);
      continue;
    }
    if (old) fail("N\xE3o \xE9 permitido alterar confirma\xE7\xE3o existente. Desfa\xE7a e registre novamente.");
    if (!supervisors.includes(x2.supervisor)) fail("Supervisor inv\xE1lido na confirma\xE7\xE3o sem convoca\xE7\xE3o.");
    date(x2.dataServico);
    if (typeof x2.unidade !== "string" || !base.units.includes(x2.unidade)) fail("Unidade inv\xE1lida na confirma\xE7\xE3o sem convoca\xE7\xE3o.");
    if (session.role !== "CONTROLADORIA" && (session.role !== "SUPERVISOR" || x2.supervisor !== session.user)) fail("Somente o supervisor respons\xE1vel pode confirmar sua unidade.", 403);
    const owner = base.unitOwners?.[x2.unidade];
    if (owner && owner !== x2.supervisor) fail("Esta unidade est\xE1 atribu\xEDda a outro supervisor.", 403);
    if (next.convocacoes.some((c) => c.supervisor === x2.supervisor && c.unidade === x2.unidade && c.dataServico === x2.dataServico)) fail("J\xE1 existe convoca\xE7\xE3o nesta unidade e data. Desfa\xE7a a confirma\xE7\xE3o antes de convocar.");
    savedNoConv.push({ supervisor: x2.supervisor, unidade: x2.unidade, dataServico: x2.dataServico, registradoEm: timestamp, registradoPor: session.user });
  }
  for (const old of baseNoConv) {
    if (incomingKeys.has(noConvKey(old))) continue;
    if (session.role !== "CONTROLADORIA" && (session.role !== "SUPERVISOR" || old.supervisor !== session.user)) fail("Sem permiss\xE3o para desfazer confirma\xE7\xE3o de outro supervisor.", 403);
  }
  const noConvChanged = !same(savedNoConv, baseNoConv);
  if (session.role !== "CONTROLADORIA") {
    for (const k of ["units", "teamsConfig", "unitOwners", "teamsAutomation", "teamsMessage", "teamsHistory"]) if (!same(next[k] ?? base[k], base[k])) fail("Sem permiss\xE3o para alterar configura\xE7\xF5es.", 403);
    if (noConvChanged) {
      const config = db.raw.settings[0]?.data || {};
      add("aproar_web_settings", "update", 1, { data: { ...config, semConvocacoesUnidade: savedNoConv } });
    }
  } else {
    for (const [s, x2] of Object.entries(next.teamsConfig || {})) {
      const previous = base.teamsConfig?.[s];
      if (!supervisors.includes(s)) {
        if (!previous || !same(x2, previous)) fail("Supervisor inv\xE1lido.");
        continue;
      }
      if (!same(x2, previous)) {
        if (x2.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(x2.email)) fail("E-mail inv\xE1lido.");
        add("engenheiros_teams", "update", s, { email_teams: x2.email || "", ativo: x2.ativo !== false });
      }
    }
    const units = next.units ?? base.units;
    const originalUnits = new Set(base.units);
    if (!Array.isArray(units) || units.length > 500 || units.some((u) => typeof u !== "string" || !u.trim() || u.length > 200 && !originalUnits.has(u)) || new Set(units.map(clean)).size !== units.length || next.obras.some((o) => !units.includes(o.unidade) && oldWorks.get(String(o.id))?.unidade !== o.unidade)) fail("Cadastro de unidades inv\xE1lido.");
    for (const removed of base.units.filter((u) => !units.includes(u))) {
      if (base.obras.some((o) => o.unidade === removed) || db.state.convocacoes.some((c) => c.unidade === removed) || db.raw.servicos_apontamento.some((s) => s.unidade_snapshot === removed) || db.state.conflitosTentados.some((c) => c.unidade === removed || c.unidadeExistente === removed)) fail("Unidade possui obras ou hist\xF3rico vinculado. Remova os v\xEDnculos antes de excluir.");
    }
    const history = (next.teamsHistory || []).filter((x2) => !numericId(x2.id));
    const previousConfig = db.raw.settings[0]?.data || {};
    const persistedUnits = units.filter((u) => u.length <= 200 || Array.isArray(previousConfig.units) && previousConfig.units.includes(u));
    const config = { ...previousConfig, units: persistedUnits, unitOwners: next.unitOwners || {}, teamsAutomation: !!next.teamsAutomation, teamsMessage: next.teamsMessage || "", teamsHistory: history, ...noConvChanged ? { semConvocacoesUnidade: savedNoConv } : {} };
    if (!same(config, previousConfig)) add("aproar_web_settings", "update", 1, { data: config });
  }
  if (ops.length) add("auditoria", "insert", "audit:" + crypto.randomUUID(), { entidade: "aproar-web", entidade_id: null, acao: "SALVAR", usuario: session.user, ocorrido_em: timestamp, contexto: { perfil: session.role, operacoes: ops.map((o) => ({ tabela: o.table, acao: o.action, id: o.id })) } });
  if (ops.length > 1e4) fail("Altera\xE7\xE3o muito grande. Divida a opera\xE7\xE3o em lotes.");
  return ops;
}
__name(buildOperations, "buildOperations");

// src/admin-relocation.js
var fail2 = /* @__PURE__ */ __name((message, status = 409) => {
  throw Object.assign(new Error(message), { status });
}, "fail");
var cleanDate = /* @__PURE__ */ __name((value2) => {
  const date2 = String(value2 instanceof Date ? value2.toISOString().slice(0, 10) : value2 || "").slice(0, 10);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date2) || !Number.isFinite(Date.parse(date2 + "T12:00:00Z")) || (/* @__PURE__ */ new Date(date2 + "T12:00:00Z")).toISOString().slice(0, 10) !== date2) fail2("Informe uma data v\xE1lida para a transfer\xEAncia.", 400);
  return date2;
}, "cleanDate");
var validTurn = /* @__PURE__ */ __name((turn) => ["Integral", "Manh\xE3", "Tarde", "Noite"].includes(turn), "validTurn");
var overlap2 = /* @__PURE__ */ __name((a2, b2) => a2 === b2 || a2 === "Integral" && ["Manh\xE3", "Tarde"].includes(b2) || b2 === "Integral" && ["Manh\xE3", "Tarde"].includes(a2), "overlap");
var same2 = /* @__PURE__ */ __name((a2, b2) => String(a2 ?? "") === String(b2 ?? ""), "same");
function validateAdminRelocationInput(body) {
  if (!body || typeof body !== "object" || Array.isArray(body) || Object.keys(body).some((k) => !["requestId", "convocacaoId", "colaboradorId", "source", "destination"].includes(k)) || !/^[a-f0-9-]{36}$/i.test(body.requestId || "") || !/^\d+$/.test(String(body.convocacaoId || "")) || !/^\d+$/.test(String(body.colaboradorId || ""))) fail2("Identifica\xE7\xE3o da transfer\xEAncia inv\xE1lida.", 400);
  const s = body.source, d = body.destination;
  if (!s || !d || typeof s !== "object" || typeof d !== "object" || Array.isArray(s) || Array.isArray(d) || Object.keys(s).some((k) => !["dataServico", "unidade", "supervisor", "obraId", "turno"].includes(k)) || Object.keys(d).some((k) => !["dataServico", "unidade", "supervisor", "obraId", "turno"].includes(k)) || !isSafeUnitName(d.unidade) || !validTurn(d.turno) || !validTurn(s.turno) || ![...supervisors, "PAULO"].includes(d.supervisor) || !s.supervisor || !/^\d*$/.test(String(d.obraId ?? "")) || !/^\d*$/.test(String(s.obraId ?? "")))
    fail2("Unidade, obra, respons\xE1vel ou turno inv\xE1lido para a transfer\xEAncia.", 400);
  return {
    requestId: body.requestId,
    convocacaoId: String(body.convocacaoId),
    colaboradorId: String(body.colaboradorId),
    source: { ...s, dataServico: cleanDate(s.dataServico), obraId: String(s.obraId || "") },
    destination: { ...d, dataServico: cleanDate(d.dataServico), obraId: String(d.obraId || "") }
  };
}
__name(validateAdminRelocationInput, "validateAdminRelocationInput");
function buildAdminRelocationOperations({ current, works = [], conflicts = [], unavailable = false, request, actor, timestamp }) {
  const { source, destination: d, convocacaoId, colaboradorId, requestId } = request;
  if (!current) fail2("Convoca\xE7\xE3o n\xE3o encontrada. Recarregue e confira o registro.");
  if (!same2(current.id, convocacaoId) || !same2(current.colaborador_id, colaboradorId))
    fail2("O colaborador n\xE3o corresponde \xE0 convoca\xE7\xE3o selecionada.");
  const currentDate = cleanDate(current.data);
  const unit = String(current.unidade || "");
  const meta = metadata(current.observacao).meta;
  const visibleSourceWork = meta.servico_a_definir ? "" : String(current.obra_id || "");
  if (!same2(currentDate, source.dataServico) || !same2(unit, source.unidade) || !same2(current.engenheiro, source.supervisor) || !same2(current.turno || "Integral", source.turno) || !same2(visibleSourceWork, source.obraId))
    fail2("Esta convoca\xE7\xE3o foi alterada por outra pessoa. Atualize os dados antes de transferir.");
  if (current.has_point || current.has_services || current.custos_separados === true || meta.apontado_em)
    fail2("A convoca\xE7\xE3o possui apontamento ou v\xEDnculo hist\xF3rico. A transfer\xEAncia autom\xE1tica foi bloqueada; solicite confer\xEAncia \xE0 Controladoria.");
  if (unavailable) fail2("Este colaborador est\xE1 indispon\xEDvel na data de destino.");
  if (conflicts.some((c) => metadata(c.observacao).meta.extra_avulsa !== true && overlap2(c.turno || "Integral", d.turno)))
    fail2("A transfer\xEAncia geraria conflito: colaborador j\xE1 convocado em turno sobreposto na data de destino.");
  const available = works.filter((w) => w.unidade === d.unidade);
  if (!available.length) fail2("Cadastre uma obra na unidade de destino antes de transferir.");
  const chosen = d.obraId ? available.find((w) => same2(w.id, d.obraId)) : available[0];
  if (!chosen) fail2("A obra n\xE3o pertence \xE0 unidade de destino.");
  const assigned = Boolean(d.obraId);
  const oldObs = metadata(current.observacao);
  const previousLabel = String(oldObs.text || "").trim();
  const description = /Turno:\s*(Integral|Manhã|Tarde|Noite)/i.test(previousLabel) ? previousLabel.replace(/Turno:\s*(Integral|Manhã|Tarde|Noite)/i, "Turno: " + d.turno) : "Turno: " + d.turno + (previousLabel ? " | " + previousLabel : "");
  const newMeta = {
    ...oldObs.meta,
    servico_a_definir: !assigned,
    realocado_por: actor,
    realocado_em: timestamp
  };
  const oldValues = {
    dataServico: currentDate,
    unidade: unit,
    supervisor: current.engenheiro,
    obraId: visibleSourceWork,
    turno: current.turno || "Integral"
  };
  const newValues = {
    dataServico: d.dataServico,
    unidade: d.unidade,
    supervisor: d.supervisor,
    obraId: assigned ? String(chosen.id) : "",
    turno: d.turno
  };
  if (Object.keys(oldValues).every((k) => same2(oldValues[k], newValues[k])))
    fail2("N\xE3o h\xE1 altera\xE7\xF5es para salvar nesta transfer\xEAncia.", 400);
  return [
    {
      table: "convocacoes",
      action: "update",
      id: convocacaoId,
      data: {
        obra_id: String(chosen.id),
        data: d.dataServico,
        engenheiro: d.supervisor,
        turno: d.turno,
        observacao: description + " ||APROAR_META|| " + JSON.stringify(newMeta)
      }
    },
    {
      table: "auditoria",
      action: "insert",
      id: "audit:" + requestId,
      data: {
        entidade: "convocacoes",
        entidade_id: convocacaoId,
        acao: "REALOCACAO_ADMINISTRATIVA",
        usuario: actor,
        ocorrido_em: timestamp,
        antes: oldValues,
        depois: newValues,
        contexto: { convocacaoId, colaboradorId, motivo: "Transfer\xEAncia de funcion\xE1rio entre equipes/unidades" }
      }
    }
  ];
}
__name(buildAdminRelocationOperations, "buildAdminRelocationOperations");

// src/financial-adjust.js
var moneyFields = ["financeiro", "noturno", "acordo", "ajudaCusto"];
var invalid2 = /* @__PURE__ */ __name((message, status = 400) => {
  throw Object.assign(new Error(message), { status });
}, "invalid");
var rounded = /* @__PURE__ */ __name((value2) => Math.round(value2 * 100) / 100, "rounded");
function validateFinancialPayload(body) {
  if (!body || typeof body !== "object" || Array.isArray(body) || Object.keys(body).some((k) => !["requestId", "version", "changes"].includes(k))) invalid2("Solicita\xE7\xE3o financeira inv\xE1lida.");
  if (typeof body.requestId !== "string" || !/^[0-9a-f-]{36}$/i.test(body.requestId) || typeof body.version !== "string" || !/^[0-9a-f]{32}$/i.test(body.version)) invalid2("Identificador ou vers\xE3o da grava\xE7\xE3o inv\xE1lidos.");
  if (!Array.isArray(body.changes) || !body.changes.length || body.changes.length > 30) invalid2("Selecione at\xE9 30 apontamentos por lan\xE7amento.");
  const seen = /* @__PURE__ */ new Set();
  const changes = body.changes.map((item) => {
    if (!item || typeof item !== "object" || Array.isArray(item) || Object.keys(item).some((k) => !["convocacaoId", ...moneyFields].includes(k))) invalid2("Campos financeiros inv\xE1lidos.");
    const id2 = String(item.convocacaoId || "");
    if (!/^[1-9][0-9]{0,17}$/.test(id2) || seen.has(id2)) invalid2("Apontamento ausente ou duplicado.");
    seen.add(id2);
    const next = { convocacaoId: id2 };
    for (const key2 of moneyFields) {
      if (typeof item[key2] !== "number" || !Number.isFinite(item[key2]) || item[key2] < 0 || item[key2] > 1e7) invalid2("Informe valores financeiros v\xE1lidos.");
      next[key2] = rounded(item[key2]);
    }
    return next;
  });
  return { ...body, changes };
}
__name(validateFinancialPayload, "validateFinancialPayload");
function buildFinancialOperations(changes, rows, actor, timestamp = (/* @__PURE__ */ new Date()).toISOString()) {
  const rowByConv = new Map(rows.map((row) => [String(row.convocacao_id), row]));
  const ops = [];
  for (const entry of changes) {
    const record = rowByConv.get(entry.convocacaoId);
    if (!record) invalid2("Apontamento n\xE3o encontrado. Atualize a p\xE1gina.", 409);
    if (["Falta", "Atestado"].includes(record.status)) invalid2("N\xE3o \xE9 permitido lan\xE7ar valores para falta ou atestado.");
    if (!record.has_sebrae && entry.noturno > 0 && Math.abs(Number(record.noturno_atual || 0) - entry.noturno) > 5e-3) invalid2("Adicional noturno dispon\xEDvel somente para o SEBRAE.");
    const { text, meta } = metadata(record.observacao);
    if (entry.financeiro > 0 && entry.acordo > 0 && rounded(entry.financeiro) === rounded(entry.acordo) && !hasValidComplementApproval(meta, entry.financeiro, entry.acordo)) invalid2("Valor complementar igual ao acordo exige confirma\xE7\xE3o expl\xEDcita no Portal Financeiro.");
    const financial = { custo_pago: entry.financeiro, valor_acordo: entry.acordo, valor_adicional_noturno: entry.noturno, custo_pago_definido_financeiro: true, custos_separados: true, migracao_sebrae_noturno_v2: true };
    const nextMeta = { ...clearObsoleteApproval(meta, entry.financeiro, entry.acordo), custo_pago: entry.financeiro, valor_acordo: entry.acordo, valor_adicional_noturno: entry.noturno, valor_ajuda_custo: entry.ajudaCusto, custos_separados: true };
    ops.push({ table: "apontamentos", action: "update", id: String(record.apontamento_id), data: { ...financial, atualizado_em: timestamp } });
    ops.push(...financialHistoryEvents({
      convocationId: entry.convocacaoId,
      colaboradorId: record.colaborador_id,
      dataServico: record.data_servico,
      supervisor: record.supervisor_responsavel,
      actor,
      role: "FINANCEIRO",
      source: "Ajuste financeiro",
      timestamp,
      previous: { valor_acordo: record.acordo_atual, valor_adicional_noturno: record.noturno_atual },
      next: { valor_acordo: entry.acordo, valor_adicional_noturno: entry.noturno }
    }));
    ops.push({ table: "convocacoes", action: "update", id: entry.convocacaoId, data: { ...financial, observacao: text + " ||APROAR_META|| " + JSON.stringify(nextMeta) } });
  }
  ops.push({ table: "auditoria", action: "insert", id: "audit:" + crypto.randomUUID(), data: { entidade: "aproar-web", entidade_id: null, acao: "SALVAR", usuario: actor, ocorrido_em: timestamp, contexto: { perfil: "FINANCEIRO", operacoes: ops.map((op) => ({ tabela: op.table, acao: op.action, id: op.id })) } } });
  return ops;
}
__name(buildFinancialOperations, "buildFinancialOperations");

// src/neon-quota.js
var neonQuotaExceeded = /* @__PURE__ */ __name((error) => {
  const message = String(error?.message || "");
  const details = String(error?.detail || "");
  return /\bexceeded\s+(?:the\s+)?(?:[\w\s]+\s)?quota\b|\bexceeded\s+(?:the\s+)?(?:[\w\s]+\s)?limit\b|\bHTTP\s+status\s+402\b|\bdata\s+transfer\s+quota\b/i.test(message + " " + details) && /\bquota\b|\bneon\b|\bproject\b|\baccount\b|\bHTTP\s+status\s+402\b/i.test(message + " " + details);
}, "neonQuotaExceeded");
var neonQuotaPublicMessage = "O banco Neon atingiu o limite de uso do plano e suspendeu as conex\xF5es. N\xE3o \xE9 um erro de senha. O respons\xE1vel pela conta Neon precisa regularizar a cota ou aguardar a renova\xE7\xE3o do per\xEDodo. Seus registros existentes n\xE3o devem ser reenviados enquanto o banco estiver indispon\xEDvel.";

// src/auth.js
var encode = /* @__PURE__ */ __name((v2) => btoa(String.fromCharCode(...new TextEncoder().encode(JSON.stringify(v2)))).replaceAll("+", "-").replaceAll("/", "_").replace(/=+$/, ""), "encode");
var decode = /* @__PURE__ */ __name((v2) => JSON.parse(new TextDecoder().decode(Uint8Array.from(atob(v2.replaceAll("-", "+").replaceAll("_", "/")), (c) => c.charCodeAt(0)))), "decode");
var secretKey = /* @__PURE__ */ __name((env) => env.SESSION_SECRET || env.CONNECTION_CHECK_TOKEN, "secretKey");
var key = /* @__PURE__ */ __name(async (env) => crypto.subtle.importKey("raw", new TextEncoder().encode(secretKey(env)), { name: "HMAC", hash: "SHA-256" }, false, ["sign", "verify"]), "key");
async function equalSecret(a2, b2) {
  if (!a2 || !b2) return false;
  const hash = /* @__PURE__ */ __name((v2) => crypto.subtle.digest("SHA-256", new TextEncoder().encode(v2)), "hash");
  const [x2, y2] = await Promise.all([hash(a2), hash(b2)]);
  const aa = new Uint8Array(x2), bb = new Uint8Array(y2);
  let diff = 0;
  for (let i = 0; i < aa.length; i++) diff |= aa[i] ^ bb[i];
  return diff === 0;
}
__name(equalSecret, "equalSecret");
async function verifySupervisorPassword(sql, user, password) {
  if (!sql || typeof password !== "string" || !password)
    throw Object.assign(Error("Supervisor ou chave de acesso inv\xE1lidos."), { status: 401 });
  let rows;
  try {
    rows = await sql`SELECT (password_hash_bcrypt IS NOT NULL AND password_hash_bcrypt=public.crypt(${password},password_hash_bcrypt)) AS password_matches
   FROM public.aproar_supervisor_access WHERE supervisor=${user} AND active=true LIMIT 1`;
  } catch (error) {
    if (neonQuotaExceeded(error)) throw Object.assign(Error(neonQuotaPublicMessage), { status: 503, code: "NEON_QUOTA_EXCEEDED" });
    throw Object.assign(Error("N\xE3o foi poss\xEDvel validar a chave de acesso. Confira a configura\xE7\xE3o do Neon."), { status: 503 });
  }
  if (rows?.[0]?.password_matches !== true)
    throw Object.assign(Error("Supervisor ou chave de acesso inv\xE1lidos."), { status: 401 });
}
__name(verifySupervisorPassword, "verifySupervisorPassword");
async function login(body, env, sql = null) {
  if (!secretKey(env)) throw Object.assign(Error("Configure CONNECTION_CHECK_TOKEN ou SESSION_SECRET."), { status: 503 });
  const role = body.role;
  let pass, user = role;
  if (role === "CONTROLADORIA") pass = env.ADMIN_PASSWORD;
  else if (role === "FINANCEIRO") pass = env.FINANCE_PASSWORD;
  else if (role === "VISUALIZAR") pass = env.VIEWER_PASSWORD;
  else if (role === "SUPERVISOR") {
    user = String(body.supervisor || "").trim().toUpperCase();
    if (!["EDUARDO", "FELIPE", "GABRIEL", "JOEL", "NETO", "SOARES", "VICTOR", "DJOUNE XAVIER"].includes(user)) throw Object.assign(Error("Selecione um supervisor v\xE1lido."), { status: 401 });
    if (user === "DJOUNE XAVIER") {
      if (typeof env.DJOUNE_XAVIER_PASSWORD !== "string" || !env.DJOUNE_XAVIER_PASSWORD.length) throw Object.assign(Error("Senha do supervisor Djoune n\xE3o configurada."), { status: 503 });
      if (!await equalSecret(String(body.password || ""), env.DJOUNE_XAVIER_PASSWORD)) throw Object.assign(Error("Acesso ou senha inv\xE1lidos."), { status: 401 });
    } else await verifySupervisorPassword(sql, user, body.password);
  }
  if (role === "CONTROLADORIA" || role === "FINANCEIRO") {
    if (typeof pass !== "string" || !pass.length)
      throw Object.assign(
        Error("Senha administrativa n\xE3o configurada."),
        { status: 503 }
      );
    if (!await equalSecret(String(body.password || ""), pass))
      throw Object.assign(
        Error("Acesso ou senha inv\xE1lidos."),
        { status: 401 }
      );
  }
  if (!["CONTROLADORIA", "FINANCEIRO", "SUPERVISOR", "VISUALIZAR"].includes(role)) throw Object.assign(Error("Perfil inv\xE1lido."), { status: 401 });
  const claims = { role, user, exp: Math.floor(Date.now() / 1e3) + 8 * 3600, ...role === "SUPERVISOR" ? { supervisorPasswordAuth: true } : {} }, payload = encode(claims), signature = new Uint8Array(await crypto.subtle.sign("HMAC", await key(env), new TextEncoder().encode(payload)));
  return { session: { role, user }, cookie: `aproar_session=${payload}.${encode([...signature])}; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=28800` };
}
__name(login, "login");
async function identity(request, env) {
  try {
    if (!secretKey(env)) return null;
    const token = request.headers.get("cookie")?.match(/(?:^|;\s*)aproar_session=([^;]+)/)?.[1], parts = token?.split(".");
    if (parts?.length !== 2) return null;
    const verified = await crypto.subtle.verify("HMAC", await key(env), new Uint8Array(decode(parts[1])), new TextEncoder().encode(parts[0]));
    if (!verified) return null;
    const p2 = decode(parts[0]);
    if (p2.exp <= Date.now() / 1e3 || !["CONTROLADORIA", "FINANCEIRO", "SUPERVISOR", "VISUALIZAR"].includes(p2.role) || p2.role === "SUPERVISOR" && p2.supervisorPasswordAuth !== true) return null;
    return p2;
  } catch {
    return null;
  }
}
__name(identity, "identity");
function sameOrigin(request) {
  return request.headers.get("origin") === new URL(request.url).origin;
}
__name(sameOrigin, "sameOrigin");
var logoutCookie = "aproar_session=; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=0";

// src/environment.js
var stage = /* @__PURE__ */ __name((env) => env.APP_ENV === "producao" ? "producao" : "homologacao", "stage");
function writeControls(env) {
  const production = env.APP_ENV === "producao";
  const homologation = env.APP_ENV === "homologacao";
  const expectedHost = production ? env.PRODUCTION_EXPECTED_HOST : env.HOMOLOGATION_EXPECTED_HOST;
  let configuredHost = "";
  try {
    configuredHost = new URL(env.DATABASE_URL).hostname.toLowerCase();
  } catch {
  }
  const hostMatches = Boolean(configuredHost && expectedHost && configuredHost === String(expectedHost).trim().toLowerCase());
  const enabled = env.WRITES_ENABLED === "true";
  const approved = !production || env.PRODUCTION_WRITE_APPROVED === "true";
  return {
    production,
    homologation,
    hostMatches,
    hostConfigured: Boolean(expectedHost),
    enabled,
    approved,
    writesEnabled: Boolean((production || homologation) && enabled && approved && hostMatches)
  };
}
__name(writeControls, "writeControls");
var writes = /* @__PURE__ */ __name((env) => writeControls(env).writesEnabled, "writes");
var mayDeleteProduction = /* @__PURE__ */ __name((env) => env.APP_ENV !== "producao" || env.PRODUCTION_ALLOW_DELETE === "true", "mayDeleteProduction");
function permittedProductionDeletion(env, session, db, operations) {
  if (mayDeleteProduction(env)) return true;
  const deletions = operations.filter((op2) => op2.action === "delete");
  if (!deletions.length) return true;
  if (env.APP_ENV !== "producao") return false;
  if (deletions.every((op2) => op2.table === "servicos_apontamento")) {
    if (!["SUPERVISOR", "CONTROLADORIA"].includes(session.role) || deletions.length > 100) return false;
    const ids = /* @__PURE__ */ new Set(), oldServices = new Map(db.raw.servicos_apontamento.map((x2) => [String(x2.id), x2]));
    const affected = /* @__PURE__ */ new Set();
    for (const op2 of deletions) {
      if (ids.has(String(op2.id))) return false;
      ids.add(String(op2.id));
      const old = oldServices.get(String(op2.id));
      if (!old) return false;
      const convId = String(old.convocacao_id);
      const conv = db.raw.convocacoes.find((c) => String(c.id) === convId);
      if (!conv || session.role === "SUPERVISOR" && conv.engenheiro !== session.user) return false;
      const pointed = operations.some((x2) => x2.table === "apontamentos" && ["insert", "update"].includes(x2.action) && String(x2.data?.convocacao_id) === convId);
      const convUpdated = operations.some((x2) => x2.table === "convocacoes" && x2.action === "update" && String(x2.id) === convId);
      if (!pointed || !convUpdated) return false;
      const audit = operations.find((x2) => x2.table === "auditoria" && x2.action === "insert" && x2.data?.acao === "CORRECAO_VINCULO_SERVICO_APONTAMENTO" && String(x2.data?.contexto?.servicoId) === String(op2.id) && String(x2.data?.contexto?.convocacaoId) === convId && String(x2.data?.antes?.obraId) === String(old.obra_id || "") && String(x2.data?.antes?.periodo || "") === String(old.periodo || "") && String(x2.data?.antes?.unidade || "") === String(old.unidade_snapshot || "") && String(x2.data?.usuario) === session.user);
      if (!audit) return false;
      affected.add(convId);
    }
    for (const convId of affected) {
      const pointOp = operations.find((x2) => x2.table === "apontamentos" && ["insert", "update"].includes(x2.action) && String(x2.data?.convocacao_id) === convId);
      const persisted = db.raw.servicos_apontamento.filter((x2) => String(x2.convocacao_id) === convId && !ids.has(String(x2.id))).length;
      const incoming = operations.filter((x2) => x2.table === "servicos_apontamento" && x2.action === "insert" && String(x2.data?.convocacao_id) === convId).length;
      if (!["Falta", "Atestado"].includes(pointOp?.data?.status) && persisted + incoming < 1) return false;
    }
    return true;
  }
  if (session.role !== "CONTROLADORIA") return false;
  const safeWork = /* @__PURE__ */ __name((id2) => {
    if (!/^[0-9]+$/.test(id2) || !db.raw.obras.some((o) => String(o.id) === id2)) return false;
    if (db.raw.convocacoes.some((c) => String(c.obra_id) === id2)) return false;
    if (db.raw.servicos_apontamento.some((s) => String(s.obra_id) === id2)) return false;
    if (db.state.apontamentos.some((a2) => a2.itens.some((i) => i.servicos?.some((s) => String(s.obraId) === id2)))) return false;
    return true;
  }, "safeWork");
  if (deletions.every((op2) => op2.table === "obras")) {
    const unique2 = new Set(deletions.map((op2) => op2.id));
    return deletions.length <= 50 && unique2.size === deletions.length && deletions.every((op2) => safeWork(op2.id));
  }
  if (deletions.length !== 1) return false;
  const op = deletions[0];
  if (op.table !== "convocacoes" || !/^[0-9]+$/.test(op.id)) return false;
  const existing = db.raw.convocacoes.find((c) => String(c.id) === op.id);
  if (!existing) return false;
  if (db.raw.apontamentos.some((a2) => String(a2.convocacao_id) === op.id)) return false;
  if (db.raw.servicos_apontamento.some((s) => String(s.convocacao_id) === op.id)) return false;
  if (db.state.apontamentos.some((a2) => String(a2.convocacaoId) === op.id)) return false;
  if (db.raw.conflitos_convocacao.some((c) => String(c.convocacao_existente_id) === op.id)) return false;
  return true;
}
__name(permittedProductionDeletion, "permittedProductionDeletion");

// src/trello.js
var URL_TRELLO = "https://trello.com/b/TX8hGvmI.json";
var norm = /* @__PURE__ */ __name((x2) => String(x2 || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toUpperCase().trim().replace(/\s+/g, " "), "norm");
var UNITS = [
  ["MARACANA\xDA", ["APRL005", "MARACANAU"]],
  ["PARTICULAR", ["APARTAMENTO 701", "PARTICULAR"]],
  ["SEBRAE", ["SEBRAE"]],
  ["UNIFOR", ["UNIFOR"]],
  ["IDALYA E MATHEUS", ["IDALYA E MATHEUS", "IDALYA", "MATHEUS"]],
  ["COLISEU", ["COLISEU"]],
  ["BARRA DO CEAR\xC1", ["BARRA DO CEARA"]],
  ["MUSEU", ["MUSEU"]],
  ["HORIZONTE", ["HORIZONTE"]],
  ["ESCRIT\xD3RIO", ["ESCRITORIO"]],
  ["PARANGABA", ["PARANGABA"]],
  ["CENTRO", ["CENTRO"]],
  ["FIEC", ["CASA DA INDUSTRIA", "FIEC", "SESI DR", "CONDOMINIO"]]
];
var tokens = /* @__PURE__ */ __name((text) => {
  const t = norm(text), found = [];
  for (const [unit, names] of UNITS) for (const name of names) {
    let i = t.indexOf(norm(name));
    while (i >= 0) {
      if (!/[A-Z0-9]/.test(t[i - 1] || "") && !/[A-Z0-9]/.test(t[i + norm(name).length] || "")) found.push({ unit, i });
      i = t.indexOf(norm(name), i + norm(name).length);
    }
  }
  return found.sort((a2, b2) => a2.i - b2.i);
}, "tokens");
var unique = /* @__PURE__ */ __name((values) => [...new Set(values)], "unique");
function detect(text) {
  const t = norm(text);
  if (!t) return null;
  for (const m of t.matchAll(/(?:UNIDADE(?:\s+DA\s+OBRA)?|UNID\.?|LOCAL|SITE)\s*(?:DA\s+OBRA\s*)?[:=\-]?\s*/g)) {
    const ts2 = tokens(t.slice(m.index + m[0].length, m.index + m[0].length + 160));
    if (ts2.length) return (ts2.find((x2) => x2.unit !== "FIEC") || ts2[0]).unit;
  }
  for (const part of t.split("|")) {
    const physical2 = tokens(part).filter((x2) => x2.unit !== "FIEC");
    if (physical2.length) return physical2[0].unit;
  }
  const all = unique(tokens(t).map((x2) => x2.unit)), physical = all.filter((x2) => x2 !== "FIEC");
  if (physical.length === 1) return physical[0];
  if (all.length === 1 && all[0] === "FIEC") return "FIEC";
  return null;
}
__name(detect, "detect");
var unidadeCard = /* @__PURE__ */ __name((card) => detect(card.name) || detect(card.desc) || "N\xC3O IDENTIFICADA", "unidadeCard");
var URL_TRELLO_API = "https://api.trello.com/1/boards/TX8hGvmI?fields=id,name&lists=all&cards=all&card_fields=id,idList,name,desc,closed&list_fields=id,name,closed";
async function lerJSONTrello(url, fetcher) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 16e3);
  try {
    let res;
    try {
      res = await fetcher(url, { signal: ctrl.signal, headers: { accept: "application/json" } });
    } catch (e) {
      throw Error(e?.name === "AbortError" ? "O Trello demorou mais de 16 segundos para responder." : "N\xE3o foi poss\xEDvel estabelecer a conex\xE3o entre a Cloudflare e o Trello.");
    }
    if (!res.ok) throw Error("O Trello retornou HTTP " + res.status + ".");
    const size = Number(res.headers.get("content-length") || 0);
    if (size > 14e6) throw Error("Quadro Trello muito grande.");
    const mime = res.headers.get("content-type") || "";
    if (/text\/html/i.test(mime)) throw Error("O Trello retornou HTML em vez de JSON.");
    let body;
    try {
      body = await res.json();
    } catch {
      throw Error("O Trello respondeu, mas n\xE3o enviou um JSON v\xE1lido.");
    }
    if (!body || !Array.isArray(body.lists) || !Array.isArray(body.cards) || body.cards.length > 1e4) throw Error("O Trello respondeu com listas/cards inv\xE1lidos ou excessivos.");
    return body;
  } finally {
    clearTimeout(timer);
  }
}
__name(lerJSONTrello, "lerJSONTrello");
async function consultarTrello(fetcher = fetch) {
  const candidates = [{ url: URL_TRELLO_API, source: "api.trello.com" }, { url: URL_TRELLO, source: "trello.com" }];
  const errors = [];
  for (const c of candidates) {
    try {
      const data = await lerJSONTrello(c.url, fetcher);
      return {
        origem: c.source,
        lists: data.lists.filter((x2) => !x2.closed).map((x2) => ({ id: String(x2.id), name: String(x2.name || "") })),
        cards: data.cards.filter((x2) => !x2.closed).map((x2) => ({ id: String(x2.id), idList: String(x2.idList), name: String(x2.name || "").slice(0, 480), desc: String(x2.desc || "").slice(0, 6e3) }))
      };
    } catch (e) {
      console.warn("APROAR Trello read fallback:", c.source, String(e?.message || "").slice(0, 180));
      errors.push(c.source + ": " + String(e?.message || "falha desconhecida"));
    }
  }
  throw Object.assign(Error("Falha ao consultar o Trello. " + errors.join(" | ").slice(0, 480)), { status: 502 });
}
__name(consultarTrello, "consultarTrello");
function selecionar(board, filter = {}) {
  if (filter.cardId) {
    const found = board.cards.filter((c) => c.id === filter.cardId);
    if (!found.length) throw Object.assign(Error("Card n\xE3o encontrado."), { status: 404 });
    return { cards: found, origem: "Card: " + found[0].name };
  }
  const list = filter.listId ? board.lists.find((l) => l.id === filter.listId) : board.lists.find((l) => norm(l.name) === "EM EXECUCAO") || board.lists.find((l) => norm(l.name).includes("EM EXECUCAO"));
  if (!list) throw Object.assign(Error("Lista EM EXECU\xC7\xC3O n\xE3o encontrada."), { status: 404 });
  return { cards: board.cards.filter((c) => c.idList === list.id && c.name), origem: "Lista: " + list.name };
}
__name(selecionar, "selecionar");
function planejar(works, cards) {
  const updates = [], inserts = [], skipped = [], unchanged = [];
  for (const card of cards) {
    const name = card.name.trim(), unit = unidadeCard(card);
    if (!isSafeUnitName(unit)) {
      skipped.push({ nome: name, motivo: "Unidade inv\xE1lida retornada pelo Trello" });
      continue;
    }
    let item = works.find((w) => w.trello_card_id === card.id);
    if (!item) {
      let matches = works.filter((w) => !w.trello_card_id && norm(w.nome) === norm(name) && norm(w.unidade) === norm(unit));
      if (matches.length === 1) item = matches[0];
      else if (matches.length > 1) {
        skipped.push({ nome: name, motivo: "Obra legada amb\xEDgua" });
        continue;
      }
    }
    if (!item) {
      const matches = works.filter((w) => !w.trello_card_id && norm(w.nome) === norm(name));
      if (matches.length === 1) item = matches[0];
      else if (matches.length > 1) {
        skipped.push({ nome: name, motivo: "Nome duplicado sem identifica\xE7\xE3o Trello" });
        continue;
      }
    }
    if (item) {
      const target = item.trello_unidade_manual ? item.unidade : unit;
      if (!isSafeUnitName(target)) {
        skipped.push({ nome: name, motivo: "Unidade vinculada inv\xE1lida; conferir cadastro" });
        continue;
      }
      if (item.nome === name && norm(item.unidade) === norm(target) && item.trello_card_id === card.id && item.trello_list_id === card.idList) {
        unchanged.push(card);
        continue;
      }
      updates.push({ card, id: String(item.id), unit: target });
      Object.assign(item, { nome: name, unidade: target, trello_card_id: card.id, trello_list_id: card.idList });
    } else {
      if (works.some((w) => norm(w.nome) === norm(name) && w.trello_card_id && w.trello_card_id !== card.id)) {
        skipped.push({ nome: name, motivo: "Nome associado a outro card" });
        continue;
      }
      inserts.push({ card, unit });
      works.push({ nome: name, unidade: unit, trello_card_id: card.id, trello_list_id: card.idList });
    }
  }
  return { updates, inserts, skipped, unchanged };
}
__name(planejar, "planejar");
async function sincronizarTrello(sql, filter = {}, fetcher = fetch) {
  const board = await consultarTrello(fetcher), selected = selecionar(board, filter);
  if (selected.cards.length > 450) throw Object.assign(Error("Lista extensa demais para uma grava\xE7\xE3o \xFAnica."), { status: 413 });
  const current = await sql`SELECT id,nome,unidade,trello_card_id,trello_list_id,trello_unidade_manual FROM obras`;
  const p2 = planejar(current.map((x2) => ({ ...x2 })), selected.cards);
  const sqls = [sql`SELECT pg_advisory_xact_lock(hashtext('aproar-trello-obras'))`, sql`LOCK TABLE obras IN SHARE ROW EXCLUSIVE MODE`];
  for (const x2 of p2.updates) sqls.push(sql`UPDATE obras SET nome=${x2.card.name},unidade=${x2.unit},trello_card_id=${x2.card.id},trello_list_id=${x2.card.idList},trello_sync_em=NOW() WHERE id=${x2.id}::bigint RETURNING id`);
  for (const x2 of p2.inserts) sqls.push(sql`INSERT INTO obras(nome,unidade,trello_card_id,trello_list_id,trello_sync_em) VALUES (${x2.card.name},${x2.unit},${x2.card.id},${x2.card.idList},NOW()) ON CONFLICT DO NOTHING RETURNING id`);
  const report = { origem: selected.origem, recebidos: selected.cards.length, atualizadas: p2.updates.length, novas: 0, jaExistentes: p2.unchanged.length, ignoradas: p2.skipped };
  sqls.push(sql`INSERT INTO trello_snapshot(snapshot_id,listas,cards,atualizado_em,sincronizado_obras_em,ultima_tentativa_obras_em,ultimo_resultado_obras) VALUES (1,${JSON.stringify(board.lists)}::jsonb,${JSON.stringify(board.cards)}::jsonb,NOW(),NOW(),NOW(),${JSON.stringify(report)}::jsonb) ON CONFLICT(snapshot_id) DO UPDATE SET listas=excluded.listas,cards=excluded.cards,atualizado_em=NOW(),sincronizado_obras_em=NOW(),ultima_tentativa_obras_em=NOW(),ultimo_resultado_obras=excluded.ultimo_resultado_obras`);
  const rows = await sql.transaction(sqls, { isolationLevel: "ReadCommitted" });
  report.novas = p2.inserts.reduce((n, x2, i) => n + Number((rows[2 + p2.updates.length + i] || []).length > 0), 0);
  p2.inserts.forEach((x2, i) => {
    if (!(rows[2 + p2.updates.length + i] || []).length) report.ignoradas.push({ nome: x2.card.name, motivo: "Conflito com obra existente; n\xE3o alterada" });
  });
  return report;
}
__name(sincronizarTrello, "sincronizarTrello");

// src/worker.js
var common = { "cache-control": "no-store", "x-content-type-options": "nosniff", "referrer-policy": "same-origin" };
var json = /* @__PURE__ */ __name((data, status = 200, extra = {}) => new Response(JSON.stringify(data), { status, headers: { ...common, "content-type": "application/json; charset=utf-8", ...extra } }), "json");
var sha = /* @__PURE__ */ __name(async (v2) => [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(v2)))].map((x2) => x2.toString(16).padStart(2, "0")).join(""), "sha");
var failedLogins = /* @__PURE__ */ new Map();
async function applyCatalogRegistration(sql, requestId, actor, digest, operationsForCurrentState) {
  for (let attempt = 0; attempt < 3; attempt++) {
    const current = await sql`SELECT aproar_web_fingerprint() AS version`;
    const operations = await operationsForCurrentState();
    try {
      const applied = await sql`SELECT aproar_web_apply(${current[0].version},${requestId},${actor},${digest},${JSON.stringify(operations)}::jsonb) AS result`;
      return applied[0].result;
    } catch (error) {
      if (!String(error?.message || "").includes("APROAR_STALE") || attempt === 2) throw error;
    }
  }
}
__name(applyCatalogRegistration, "applyCatalogRegistration");
function limit(request) {
  const ip = request.headers.get("cf-connecting-ip") || "unknown", time = Date.now(), entry = failedLogins.get(ip);
  if (entry && entry.until > time && entry.n >= 10) return false;
  if (!entry || entry.until < time) failedLogins.set(ip, { n: 0, until: time + 6e4 });
  failedLogins.get(ip).n++;
  if (failedLogins.size > 5e3) failedLogins.clear();
  return true;
}
__name(limit, "limit");
async function bodyJSON(request) {
  if (Number(request.headers.get("content-length") || 0) > 8e6) throw Object.assign(Error("Dados muito grandes. Divida a opera\xE7\xE3o."), { status: 413 });
  const text = await request.text();
  if (text.length > 8e6) throw Object.assign(Error("Dados muito grandes."), { status: 413 });
  try {
    return JSON.parse(text);
  } catch {
    throw Object.assign(Error("Requisi\xE7\xE3o inv\xE1lida."), { status: 400 });
  }
}
__name(bodyJSON, "bodyJSON");
function summary(db, session, env) {
  return { state: visibleState(db, session), version: db.version, session: { role: session.role, user: session.user }, supervisors, writesEnabled: writes(env), stage: stage(env) };
}
__name(summary, "summary");
var worker_default = {
  async fetch(request, env) {
    const url = new URL(request.url), path = url.pathname;
    let loginStage = "request", session = null;
    try {
      if (path === "/api/health" && request.method === "GET") return json({ application: "APROAR", stage: stage(env), databaseConfigured: Boolean(env.DATABASE_URL), writesEnabled: writes(env) });
      if (path === "/api/login" && request.method === "POST") {
        loginStage = "check-origin";
        if (!sameOrigin(request)) return json({ error: "Origem n\xE3o autorizada." }, 403);
        loginStage = "rate-limit";
        if (!limit(request)) return json({ error: "Muitas tentativas. Aguarde um minuto." }, 429);
        loginStage = "parse-request";
        const body = await bodyJSON(request);
        let authSql = null;
        if (body.role === "SUPERVISOR") {
          loginStage = "check-database-config";
          if (!env.DATABASE_URL) return json({ error: "Banco n\xE3o configurado para validar a chave do supervisor." }, 503);
          loginStage = "create-database-client";
          authSql = ys(env.DATABASE_URL);
        }
        loginStage = "authenticate";
        const result = await login(body, env, authSql);
        loginStage = "format-response";
        return json({ session: result.session }, 200, { "set-cookie": result.cookie });
      }
      if (path === "/api/logout" && request.method === "POST") {
        if (!sameOrigin(request)) return json({ error: "Origem n\xE3o autorizada." }, 403);
        return json({ ok: true }, 200, { "set-cookie": logoutCookie });
      }
      if (path === "/api/check-database" || path === "/api/preview-data") {
        if (request.method !== "POST") return json({ error: "M\xE9todo n\xE3o permitido." }, 405);
        if (!env.DATABASE_URL || !env.CONNECTION_CHECK_TOKEN) return json({ error: "Configure DATABASE_URL e CONNECTION_CHECK_TOKEN." }, 503);
        if (!await equalSecret(request.headers.get("authorization")?.replace(/^Bearer /, ""), env.CONNECTION_CHECK_TOKEN)) return json({ error: "Acesso n\xE3o autorizado." }, 401);
        const sql = ys(env.DATABASE_URL);
        if (path === "/api/preview-data") {
          const db = await readDatabase(sql);
          return json({ writesEnabled: false, data: db.state });
        }
        const columns = await sql`SELECT table_name,column_name FROM information_schema.columns WHERE table_schema='public' AND table_name IN ('colaboradores','obras','convocacoes','apontamentos','servicos_apontamento')`;
        const expected = { colaboradores: ["id", "nome", "funcao", "valor_diaria", "ativo"], obras: ["id", "nome", "unidade"], convocacoes: ["id", "obra_id", "colaborador_id", "data", "engenheiro", "turno"], apontamentos: ["convocacao_id", "data_servico", "status", "custo_pago", "valor_extra", "valor_acordo", "valor_adicional_noturno"], servicos_apontamento: ["convocacao_id", "obra_id", "periodo", "principal"] }, missing = [];
        for (const [table, fields2] of Object.entries(expected)) for (const f of fields2) if (!columns.some((c) => c.table_name === table && c.column_name === f)) missing.push(table + "." + f);
        return json({ connected: true, schemaCompatible: !missing.length, missingColumns: missing, writesEnabled: writes(env) });
      }
      if (path.startsWith("/api/")) {
        session = await identity(request, env);
        if (!session) return json({ error: "Fa\xE7a login para acessar a plataforma." }, 401);
        if (path === "/api/homologacao/diagnostico" && request.method === "GET") {
          if (session.role !== "CONTROLADORIA") return json({ error: "Diagn\xF3stico restrito \xE0 Controladoria." }, 403);
          const controls = writeControls(env);
          return json({
            bancoConfigurado: Boolean(env.DATABASE_URL),
            enderecoBancoValido: controls.hostMatches || Boolean(env.DATABASE_URL),
            ambienteHomologacao: controls.homologation,
            ambienteProducao: controls.production,
            gravacaoHabilitadaNaCloudflare: controls.enabled,
            aprovacaoProducao: controls.approved,
            hostEsperadoConfigurado: controls.hostConfigured,
            hostConfere: controls.hostMatches,
            writesEnabled: controls.writesEnabled
          });
        }
        if (!env.DATABASE_URL) return json({ error: "Banco n\xE3o configurado." }, 503);
        const sql = ys(env.DATABASE_URL);
        if (path === "/api/trello/lists" && request.method === "GET") {
          if (session.role !== "CONTROLADORIA") return json({ error: "Somente a Controladoria pode consultar as listas do Trello." }, 403);
          const board = await consultarTrello();
          return json({ lists: board.lists, cards: board.cards.map((c) => ({ id: c.id, idList: c.idList, name: c.name, unidade: unidadeCard(c) })) });
        }
        if (path === "/api/trello/sync" && request.method === "POST") {
          if (session.role !== "CONTROLADORIA") return json({ error: "Somente a Controladoria pode sincronizar o Trello." }, 403);
          if (!sameOrigin(request)) return json({ error: "Origem n\xE3o autorizada." }, 403);
          if (!writes(env)) return json({ error: "Sincroniza\xE7\xE3o bloqueada: confirme o ambiente, o hostname do Neon e a autoriza\xE7\xE3o de grava\xE7\xE3o." }, 403);
          const payload = await bodyJSON(request);
          if (!payload || typeof payload !== "object" || Object.keys(payload).some((x2) => !["listId", "cardId"].includes(x2))) return json({ error: "Solicita\xE7\xE3o de sincroniza\xE7\xE3o inv\xE1lida." }, 400);
          for (const field2 of ["listId", "cardId"]) if (payload[field2] != null && (typeof payload[field2] !== "string" || payload[field2].length > 128)) return json({ error: "Identificador do Trello inv\xE1lido." }, 400);
          const result = await sincronizarTrello(sql, { listId: payload.listId, cardId: payload.cardId });
          return json({ ok: true, ...result });
        }
        const readOptions = session.role === "FINANCEIRO" ? { includeAudit: false } : session.role === "SUPERVISOR" ? { auditUser: session.user } : {};
        if (path === "/api/bootstrap" && request.method === "GET") return json(summary(await readDatabase(sql, readOptions), session, env));
        if (path === "/api/financial-history" && request.method === "GET") {
          if (session.role !== "FINANCEIRO") return json({ error: "Hist\xF3rico restrito ao Financeiro." }, 403);
          const inicio = url.searchParams.get("inicio") || "", fim = url.searchParams.get("fim") || "";
          const validDate = /* @__PURE__ */ __name((value2) => /^\d{4}-\d{2}-\d{2}$/.test(value2) && !Number.isNaN(Date.parse(value2 + "T12:00:00Z")), "validDate");
          if (!validDate(inicio) || !validDate(fim) || inicio > fim) return json({ error: "Informe um per\xEDodo v\xE1lido." }, 400);
          const logs = await sql`
     SELECT au.id::text AS id,au.contexto->>'dataServico' AS data_servico,
       co.nome AS colaborador,au.contexto->>'tipo' AS tipo,
       au.contexto->>'operacao' AS operacao,
       au.contexto->>'valorAnterior' AS valor_anterior,
       au.contexto->>'valorNovo' AS valor_novo,
       au.contexto->>'supervisorResponsavel' AS supervisor,
       au.usuario AS usuario,au.ocorrido_em AS registrado_em,
       au.contexto->>'origem' AS origem,
       au.contexto->>'convocacaoId' AS convocacao_id
     FROM auditoria au
     LEFT JOIN colaboradores co ON co.id::text=au.contexto->>'colaboradorId'
     WHERE au.acao='LANCAMENTO_FINANCEIRO_ITEM'
       AND au.contexto->>'dataServico'>=${inicio}
       AND au.contexto->>'dataServico'<=${fim}
     ORDER BY au.id DESC LIMIT 501`;
          const older = await sql`
     SELECT a.id::text AS id,a.data_servico::text AS data_servico,
       co.nome AS colaborador,category.tipo,
       category.valor::text AS valor_novo,
       a.engenheiro AS supervisor,
       a.apontado_por AS usuario_apontamento
     FROM apontamentos a
     JOIN colaboradores co ON co.id::text=a.colaborador_id
     CROSS JOIN LATERAL (
       VALUES ('Extra'::text,COALESCE(a.valor_extra,0)),
         ('Bonificação / acordo'::text,COALESCE(a.valor_acordo,0)),
         ('Adicional noturno'::text,COALESCE(a.valor_adicional_noturno,0))
     ) AS category(tipo,valor)
     WHERE a.data_servico>=${inicio}::date AND a.data_servico<=${fim}::date
       AND category.valor>0
       AND NOT EXISTS(
         SELECT 1 FROM auditoria au WHERE au.acao='LANCAMENTO_FINANCEIRO_ITEM'
          AND au.contexto->>'tipo'=category.tipo
          AND au.contexto->>'colaboradorId'=a.colaborador_id
          AND au.contexto->>'dataServico'=a.data_servico::text
          AND (au.contexto->>'convocacaoId'=a.convocacao_id
               OR au.contexto->>'supervisorResponsavel'=a.engenheiro)
       )
     ORDER BY a.data_servico DESC,a.id DESC LIMIT 501`;
          return json({
            ok: true,
            eventos: logs.slice(0, 500),
            anteriores: older.slice(0, 500),
            limiteAtingido: logs.length > 500 || older.length > 500
          });
        }
        if (path === "/api/financial-release" && request.method === "GET") {
          if (!["SUPERVISOR", "CONTROLADORIA", "FINANCEIRO"].includes(session.role)) return json({ error: "Acesso n\xE3o autorizado." }, 403);
          const events = await sql`SELECT a.acao,a.usuario,a.ocorrido_em,a.contexto
      FROM auditoria a WHERE a.acao IN ('SOLICITACAO_LIBERACAO_FINANCEIRA','LIBERACAO_FINANCEIRA_AUTORIZADA',
        'LIBERACAO_FINANCEIRA_NEGADA','LIBERACAO_FINANCEIRA_UTILIZADA')
      ORDER BY a.id ASC LIMIT 20000`;
          const all = releaseState(events).filter((r) => session.role !== "SUPERVISOR" || r.supervisor === session.user);
          const records = await sql`SELECT id::text AS id,nome FROM colaboradores`;
          const names = new Map(records.map((x2) => [x2.id, x2.nome]));
          return json({ ok: true, requests: all.map((x2) => ({
            ...x2,
            colaborador: names.get(x2.colaboradorId) || x2.colaboradorId,
            deadline: financialDeadline(x2.dataServico).limitAt
          })) });
        }
        if (path === "/api/financial-release/request" && request.method === "POST") {
          if (session.role !== "SUPERVISOR") return json({ error: "Somente supervisores solicitam libera\xE7\xE3o." }, 403);
          if (!sameOrigin(request)) return json({ error: "Origem n\xE3o autorizada." }, 403);
          if (!writes(env)) return json({ error: "Grava\xE7\xE3o indispon\xEDvel." }, 403);
          const body = await bodyJSON(request), parsed = validRequest(body);
          if (!/^[a-f0-9-]{36}$/i.test(body.requestId || "")) return json({ error: "Identificador de solicita\xE7\xE3o inv\xE1lido." }, 400);
          if (!afterFinancialDeadline(parsed.dataServico, (/* @__PURE__ */ new Date()).toISOString()))
            return json({ error: "O prazo financeiro ainda est\xE1 aberto. N\xE3o \xE9 necess\xE1rio solicitar autoriza\xE7\xE3o." }, 400);
          const candidates = await sql`SELECT c.id,c.colaborador_id,c.observacao FROM convocacoes c
      WHERE (c.colaborador_id::text=${parsed.colaboradorId} OR c.colaborador_id IS NULL)
      AND c.data=${parsed.dataServico}::date AND c.engenheiro=${session.user}`;
          const matched = candidates.some((c) => String(c.colaborador_id ?? "") === parsed.colaboradorId || String(metadata(c.observacao).meta.avulso_eventual?.id || "") === parsed.colaboradorId);
          if (!matched) return json({ error: "Colaborador ou avulso sem convoca\xE7\xE3o vinculada a este supervisor e data." }, 403);
          const exists = await sql`SELECT 1 FROM auditoria WHERE acao='SOLICITACAO_LIBERACAO_FINANCEIRA'
      AND contexto->>'supervisor'=${session.user} AND contexto->>'colaboradorId'=${parsed.colaboradorId}
      AND contexto->>'dataServico'=${parsed.dataServico}
      AND contexto->'fields'=${JSON.stringify(parsed.fields)}::jsonb
      AND NOT EXISTS (SELECT 1 FROM auditoria f WHERE f.acao IN ('LIBERACAO_FINANCEIRA_UTILIZADA','LIBERACAO_FINANCEIRA_NEGADA')
        AND f.contexto->>'requestId'=auditoria.contexto->>'requestId') LIMIT 1`;
          if (exists.length) return json({ error: "J\xE1 existe uma solicita\xE7\xE3o para estas colunas. Consulte o status antes de enviar outra." }, 409);
          const operations = [{
            table: "auditoria",
            action: "insert",
            id: "audit:" + body.requestId,
            data: {
              entidade: "apontamentos",
              entidade_id: parsed.colaboradorId,
              acao: "SOLICITACAO_LIBERACAO_FINANCEIRA",
              usuario: session.user,
              ocorrido_em: (/* @__PURE__ */ new Date()).toISOString(),
              contexto: { requestId: body.requestId, supervisor: session.user, ...parsed, limitAt: financialDeadline(parsed.dataServico).limitAt }
            }
          }];
          const version = await sql`SELECT aproar_web_fingerprint() AS version`;
          const digest = await sha(JSON.stringify(body));
          await sql`SELECT aproar_web_apply(${version[0].version},${body.requestId},${session.user},${digest},${JSON.stringify(operations)}::jsonb)`;
          return json({ ok: true, requestId: body.requestId });
        }
        if (path === "/api/financial-release/decide" && request.method === "POST") {
          if (!["CONTROLADORIA", "FINANCEIRO"].includes(session.role)) return json({ error: "Somente Controladoria ou Financeiro autorizam." }, 403);
          if (!sameOrigin(request)) return json({ error: "Origem n\xE3o autorizada." }, 403);
          if (!writes(env)) return json({ error: "Grava\xE7\xE3o indispon\xEDvel." }, 403);
          const body = await bodyJSON(request), requestId = String(body?.releaseId || ""), decision = body?.decision;
          if (!/^[a-f0-9-]{36}$/i.test(body?.requestId || "") || !/^[a-f0-9-]{36}$/i.test(requestId) || !["approve", "deny"].includes(decision)) return json({ error: "Decis\xE3o inv\xE1lida." }, 400);
          const events = await sql`SELECT acao,usuario,ocorrido_em,contexto FROM auditoria WHERE acao IN (
     'SOLICITACAO_LIBERACAO_FINANCEIRA','LIBERACAO_FINANCEIRA_AUTORIZADA','LIBERACAO_FINANCEIRA_NEGADA',
     'LIBERACAO_FINANCEIRA_UTILIZADA') ORDER BY id ASC LIMIT 20000`;
          const entry = releaseState(events).find((x2) => x2.id === requestId);
          if (!entry || entry.status !== "Pendente") return json({ error: "Solicita\xE7\xE3o n\xE3o est\xE1 pendente. Recarregue a lista." }, 409);
          const action = decision === "approve" ? "LIBERACAO_FINANCEIRA_AUTORIZADA" : "LIBERACAO_FINANCEIRA_NEGADA";
          const operations = [{
            table: "auditoria",
            action: "insert",
            id: "audit:" + body.requestId,
            data: {
              entidade: "apontamentos",
              entidade_id: entry.colaboradorId,
              acao: action,
              usuario: session.user,
              ocorrido_em: (/* @__PURE__ */ new Date()).toISOString(),
              contexto: {
                requestId,
                supervisor: entry.supervisor,
                colaboradorId: entry.colaboradorId,
                dataServico: entry.dataServico,
                fields: entry.fields,
                reason: String(body.reason || "").slice(0, 600)
              }
            }
          }];
          const current = await sql`SELECT aproar_web_fingerprint() AS version`, digest = await sha(JSON.stringify(body));
          await sql`SELECT aproar_web_apply(${current[0].version},${body.requestId},${session.user},${digest},${JSON.stringify(operations)}::jsonb)`;
          return json({ ok: true, requestId });
        }
        if (path === "/api/save-status" && request.method === "GET") {
          const requestId = url.searchParams.get("requestId") || "";
          if (!/^[a-f0-9-]{36}$/i.test(requestId)) return json({ error: "Identificador de salvamento inv\xE1lido." }, 400);
          const rows = await sql`SELECT 1 AS saved FROM aproar_web_requests WHERE id=${requestId} AND actor=${session.user} LIMIT 1`;
          return json({ confirmed: rows.length > 0, requestId });
        }
        if (path === "/api/financial-confirm-duplicate" && request.method === "POST") {
          if (session.role !== "FINANCEIRO") return json({ error: "Somente o Financeiro pode confirmar pagamentos distintos." }, 403);
          if (!sameOrigin(request)) return json({ error: "Origem n\xE3o autorizada." }, 403);
          if (!writes(env)) return json({ error: "Grava\xE7\xE3o n\xE3o autorizada neste ambiente." }, 403);
          const body = validateComplementConfirmation(await bodyJSON(request));
          const rows = await sql`SELECT c.id::text AS convocacao_id,c.observacao,
     c.custo_pago AS complemento_convocacao,c.valor_acordo AS acordo_convocacao,
     a.id::text AS apontamento_id,a.status,
     a.custo_pago AS complemento_atual,a.valor_acordo AS acordo_atual
     FROM convocacoes c JOIN apontamentos a ON a.convocacao_id=c.id::text
     WHERE c.id::text=${body.convocacaoId}`;
          const operations = buildComplementConfirmationOperations(body, rows[0], session.user);
          const digest = await sha(JSON.stringify(body));
          const applied = await sql`SELECT aproar_web_apply(${body.version},${body.requestId},${session.user},${digest},${JSON.stringify(operations)}::jsonb) AS result`;
          return json({ ok: true, version: applied[0].result.version });
        }
        if (path === "/api/financial-adjust" && request.method === "POST") {
          if (session.role !== "FINANCEIRO") return json({ error: "Somente o Financeiro pode lan\xE7ar pagamentos e passagens." }, 403);
          if (!sameOrigin(request)) return json({ error: "Origem n\xE3o autorizada." }, 403);
          if (!writes(env)) return json({ error: "Grava\xE7\xE3o n\xE3o autorizada neste ambiente." }, 403);
          const body = validateFinancialPayload(await bodyJSON(request));
          const ids = body.changes.map((change) => change.convocacaoId).join(",");
          const rows = await sql`SELECT c.id::text AS convocacao_id,c.observacao,a.id::text AS apontamento_id,a.status,
      c.colaborador_id::text AS colaborador_id,c.data::text AS data_servico,c.engenheiro AS supervisor_responsavel,
      a.valor_acordo AS acordo_atual,a.valor_adicional_noturno AS noturno_atual,
      (coalesce(upper(o.unidade),'')='SEBRAE' OR EXISTS(
        SELECT 1 FROM servicos_apontamento s JOIN obras so ON so.id::text=s.obra_id
        WHERE s.convocacao_id=a.convocacao_id AND upper(so.unidade)='SEBRAE'
      )) AS has_sebrae
      FROM convocacoes c JOIN apontamentos a ON a.convocacao_id=c.id::text
      LEFT JOIN obras o ON o.id=c.obra_id
      WHERE a.convocacao_id=ANY(string_to_array(${ids},','))`;
          const operations = buildFinancialOperations(body.changes, rows, session.user);
          const digest = await sha(JSON.stringify(body));
          const applied = await sql`SELECT aproar_web_apply(${body.version},${body.requestId},${session.user},${digest},${JSON.stringify(operations)}::jsonb) AS result`;
          return json({ ok: true, version: applied[0].result.version });
        }
        if (path === "/api/unit-register" && request.method === "POST") {
          if (session.role !== "CONTROLADORIA") return json({ error: "Somente a Controladoria pode cadastrar unidades." }, 403);
          if (!sameOrigin(request)) return json({ error: "Origem n\xE3o autorizada." }, 403);
          if (!writes(env)) return json({ error: "Grava\xE7\xE3o n\xE3o autorizada neste ambiente." }, 403);
          const body = await bodyJSON(request);
          if (!body || typeof body !== "object" || Array.isArray(body) || typeof body.name !== "string" || typeof body.version !== "string" || !/^[a-f0-9-]{36}$/i.test(body.requestId || ""))
            return json({ error: "Dados do cadastro de unidade inv\xE1lidos." }, 400);
          const name = body.name.trim().replace(/\s+/g, " ").toUpperCase();
          if (!name || name.length > 200 || /[<>]/.test(name) || !isSafeUnitName(name))
            return json({ error: "Informe um nome de unidade v\xE1lido (at\xE9 80 caracteres, sem links ou URLs)." }, 400);
          const digest = await sha(JSON.stringify(body));
          const previous = await sql`SELECT actor,payload_hash FROM aproar_web_requests WHERE id=${body.requestId}`;
          if (previous.length) {
            if (previous[0].actor !== session.user || previous[0].payload_hash !== digest)
              return json({ error: "Identificador de requisi\xE7\xE3o reutilizado." }, 409);
            return json({ ok: true, requestId: body.requestId, replayed: true });
          }
          const result = await applyCatalogRegistration(sql, body.requestId, session.user, digest, async () => {
            const [settings, works] = await Promise.all([
              sql`SELECT data FROM aproar_web_settings WHERE id=1`,
              sql`SELECT DISTINCT unidade FROM obras`
            ]);
            if (!settings.length) throw Object.assign(Error("Configura\xE7\xE3o de unidades indispon\xEDvel no banco."), { status: 503 });
            const config = settings[0]?.data || {};
            const configured = Array.isArray(config.units) ? config.units : [];
            const normalize = /* @__PURE__ */ __name((value2) => String(value2 || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toUpperCase().trim(), "normalize");
            if ([...configured, ...works.map((x2) => x2.unidade)].some((u) => normalize(u) === normalize(name)))
              throw Object.assign(Error("Esta unidade j\xE1 est\xE1 cadastrada."), { status: 409 });
            if (configured.length >= 500) throw Object.assign(Error("Limite de unidades cadastradas atingido."), { status: 400 });
            return [
              { table: "aproar_web_settings", action: "update", id: "1", data: { data: { ...config, units: [...configured, name] } } },
              { table: "auditoria", action: "insert", id: "audit:" + body.requestId, data: {
                entidade: "aproar-web",
                entidade_id: null,
                acao: "CADASTRAR_UNIDADE",
                usuario: session.user,
                ocorrido_em: (/* @__PURE__ */ new Date()).toISOString(),
                contexto: { nome: name }
              } }
            ];
          });
          return json({ ok: true, requestId: body.requestId, name, version: result.version });
        }
        if (path === "/api/work-register" && request.method === "POST") {
          if (session.role !== "CONTROLADORIA") return json({ error: "Somente a Controladoria pode cadastrar obras." }, 403);
          if (!sameOrigin(request)) return json({ error: "Origem n\xE3o autorizada." }, 403);
          if (!writes(env)) return json({ error: "Grava\xE7\xE3o n\xE3o autorizada neste ambiente." }, 403);
          const body = await bodyJSON(request);
          if (!body || typeof body !== "object" || Array.isArray(body) || typeof body.name !== "string" || typeof body.unit !== "string" || !/^[a-f0-9-]{36}$/i.test(body.requestId || ""))
            return json({ error: "Dados do cadastro de obra inv\xE1lidos." }, 400);
          const name = body.name.trim().replace(/\s+/g, " ");
          const unit = body.unit.trim().replace(/\s+/g, " ").toUpperCase();
          if (!name || name.length > 220 || /[<>]/.test(name) || !unit || unit.length > 200 || /[<>]/.test(unit) || !isSafeUnitName(unit))
            return json({ error: "Informe obra e unidade v\xE1lidas (at\xE9 220 e 200 caracteres)." }, 400);
          const digest = await sha(JSON.stringify(body));
          const key2 = "work:" + body.requestId;
          const previous = await sql`SELECT actor,payload_hash,result FROM aproar_web_requests WHERE id=${body.requestId}`;
          if (previous.length) {
            if (previous[0].actor !== session.user || previous[0].payload_hash !== digest)
              return json({ error: "Identificador de requisi\xE7\xE3o reutilizado." }, 409);
            return json({
              ok: true,
              requestId: body.requestId,
              replayed: true,
              obraId: previous[0].result?.ids?.[key2],
              version: previous[0].result?.version
            });
          }
          const result = await applyCatalogRegistration(sql, body.requestId, session.user, digest, async () => {
            const [matches, settings, units] = await Promise.all([
              sql`SELECT id,unidade FROM obras WHERE upper(trim(nome))=upper(trim(${name})) LIMIT 1`,
              sql`SELECT data FROM aproar_web_settings WHERE id=1`,
              sql`SELECT DISTINCT unidade FROM obras`
            ]);
            if (matches.length) throw Object.assign(Error("J\xE1 existe uma obra ou servi\xE7o com esse nome na unidade " + matches[0].unidade + "."), { status: 409 });
            const configured = Array.isArray(settings[0]?.data?.units) ? settings[0].data.units : [];
            if (![...configured, ...units.map((x2) => x2.unidade)].includes(unit))
              throw Object.assign(Error("Unidade n\xE3o cadastrada. Cadastre a unidade antes da obra."), { status: 400 });
            return [
              { table: "obras", action: "insert", id: key2, data: { nome: name, unidade: unit, trello_unidade_manual: true } },
              { table: "auditoria", action: "insert", id: "audit:" + body.requestId, data: {
                entidade: "aproar-web",
                entidade_id: null,
                acao: "CADASTRAR_OBRA",
                usuario: session.user,
                ocorrido_em: (/* @__PURE__ */ new Date()).toISOString(),
                contexto: { nome: name, unidade: unit }
              } }
            ];
          });
          return json({ ok: true, requestId: body.requestId, obraId: result.ids?.[key2], version: result.version });
        }
        if (path === "/api/indicator-dismissal" && request.method === "POST") {
          if (session.role !== "CONTROLADORIA") return json({ error: "Somente a Controladoria pode ajustar pend\xEAncias do indicador." }, 403);
          if (!sameOrigin(request)) return json({ error: "Origem n\xE3o autorizada." }, 403);
          if (!writes(env)) return json({ error: "Grava\xE7\xE3o n\xE3o autorizada neste ambiente." }, 403);
          const body = await bodyJSON(request);
          if (!body || typeof body !== "object" || Array.isArray(body) || Object.keys(body).some((k) => !["requestId", "supervisor", "dataServico", "motivo", "acao", "tipo"].includes(k)) || !/^[a-f0-9-]{36}$/i.test(body.requestId || "")) return json({ error: "Solicita\xE7\xE3o inv\xE1lida." }, 400);
          const supervisor = String(body.supervisor || "").trim().toUpperCase(), date2 = String(body.dataServico || "");
          const action = body.acao, reason = String(body.motivo || "").trim(), tipo = String(body.tipo || "convocacao");
          const validDate = /^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(date2) && !Number.isNaN(Date.parse(date2 + "T12:00:00Z")) && (/* @__PURE__ */ new Date(date2 + "T12:00:00Z")).toISOString().slice(0, 10) === date2;
          const today = new Intl.DateTimeFormat("sv-SE", { timeZone: "America/Fortaleza", year: "numeric", month: "2-digit", day: "2-digit" }).format(/* @__PURE__ */ new Date());
          if (!supervisors.includes(supervisor) || !validDate || date2 < (supervisor === "FELIPE" ? "2026-09-28" : "2026-09-16") || date2 > today || !["dispensar", "reativar"].includes(action) || !["convocacao", "apontamento"].includes(tipo) || reason.length < 5 || reason.length > 500)
            return json({ error: "Informe supervisor, data monitorada e justificativa v\xE1lida (5 a 500 caracteres)." }, 400);
          const digest = await sha(JSON.stringify(body));
          const previous = await sql`SELECT actor,payload_hash FROM aproar_web_requests WHERE id=${body.requestId}`;
          if (previous.length) {
            if (previous[0].actor !== session.user || previous[0].payload_hash !== digest) return json({ error: "Identificador de requisi\xE7\xE3o reutilizado." }, 409);
            return json({ ok: true, requestId: body.requestId, replayed: true });
          }
          await applyCatalogRegistration(sql, body.requestId, session.user, digest, async () => {
            const settings = await sql`SELECT data FROM aproar_web_settings WHERE id=1`;
            if (!settings.length) throw Object.assign(Error("Configura\xE7\xE3o de indicadores indispon\xEDvel."), { status: 503 });
            const config = settings[0].data || {};
            const field2 = tipo === "convocacao" ? "dispensasPendenciaConvocacao" : "dispensasPendenciaApontamento";
            const history = Array.isArray(config[field2]) ? config[field2] : [];
            if (history.length > 5e4) throw Object.assign(Error("Limite de dispensas atingido."), { status: 400 });
            const existing = history.find((x2) => x2.supervisor === supervisor && x2.dataServico === date2);
            if (action === "dispensar" && existing) throw Object.assign(Error("Esta data j\xE1 foi dispensada. Atualize o indicador."), { status: 409 });
            if (action === "reativar" && !existing) throw Object.assign(Error("Esta dispensa j\xE1 foi retirada. Atualize o indicador."), { status: 409 });
            if (action === "dispensar" && tipo === "convocacao") {
              const registered = await sql`SELECT id FROM convocacoes WHERE engenheiro=${supervisor} AND data=${date2}::date LIMIT 1`;
              if (registered.length) throw Object.assign(Error("J\xE1 existe convoca\xE7\xE3o nessa data. N\xE3o h\xE1 pend\xEAncia para dispensar."), { status: 409 });
              const assigned = Object.entries(config.unitOwners || {}).filter(([, owner]) => owner === supervisor).map(([unit]) => unit);
              const historic = assigned.length ? [] : await sql`SELECT DISTINCT o.unidade FROM convocacoes c JOIN obras o ON o.id=c.obra_id WHERE c.engenheiro=${supervisor}`;
              const units = assigned.length ? assigned : historic.map((x2) => x2.unidade);
              const confirmations = Array.isArray(config.semConvocacoesUnidade) ? config.semConvocacoesUnidade : [];
              const confirmed = confirmations.filter((x2) => x2.supervisor === supervisor && x2.dataServico === date2);
              const justified = units.length ? units.every((unit) => confirmed.some((x2) => x2.unidade === unit)) : confirmed.length > 0;
              if (justified) throw Object.assign(Error("A data j\xE1 foi justificada automaticamente pelo supervisor."), { status: 409 });
            }
            if (action === "dispensar" && tipo === "apontamento") {
              const pending = await sql`SELECT c.id FROM convocacoes c WHERE c.engenheiro=${supervisor} AND c.data=${date2}::date
          AND NOT EXISTS(SELECT 1 FROM apontamentos a WHERE a.convocacao_id=c.id::text) LIMIT 1`;
              if (!pending.length) throw Object.assign(Error("N\xE3o existe apontamento pendente para esse supervisor nessa data."), { status: 409 });
            }
            const now = (/* @__PURE__ */ new Date()).toISOString();
            const record = { supervisor, dataServico: date2, motivo: reason, registradoEm: now, registradoPor: session.user };
            const next = action === "dispensar" ? [...history, record] : history.filter((x2) => !(x2.supervisor === supervisor && x2.dataServico === date2));
            return [
              { table: "aproar_web_settings", action: "update", id: "1", data: { data: { ...config, [field2]: next } } },
              { table: "auditoria", action: "insert", id: "audit:" + body.requestId, data: {
                entidade: "indicador_pendencia_" + tipo,
                entidade_id: supervisor + "|" + date2,
                acao: action === "dispensar" ? "DISPENSAR_PENDENCIA_MANUAL" : "REATIVAR_PENDENCIA_MANUAL",
                usuario: session.user,
                ocorrido_em: now,
                antes: existing || null,
                depois: action === "dispensar" ? record : null,
                contexto: { supervisor, dataServico: date2, tipo, motivo: reason, origem: "controladoria_indicadores", somenteIndicador: true }
              } }
            ];
          });
          return json({ ok: true, requestId: body.requestId });
        }
        if (path === "/api/convocation-remove" && request.method === "POST") {
          if (session.role !== "CONTROLADORIA") return json({ error: "Somente a Controladoria pode remover uma inclus\xE3o de convoca\xE7\xE3o." }, 403);
          if (!sameOrigin(request)) return json({ error: "Origem n\xE3o autorizada." }, 403);
          if (!writes(env)) return json({ error: "Grava\xE7\xE3o n\xE3o autorizada neste ambiente." }, 403);
          const body = await bodyJSON(request);
          if (!body || typeof body !== "object" || Array.isArray(body) || Object.keys(body).some((k) => !["requestId", "convocacaoId", "colaboradorId"].includes(k)) || !/^[a-f0-9-]{36}$/i.test(body.requestId || "") || !/^[0-9]+$/.test(String(body.convocacaoId || "")) || !/^[0-9]+$/.test(String(body.colaboradorId || "")))
            return json({ error: "Identifica\xE7\xE3o da inclus\xE3o a remover inv\xE1lida." }, 400);
          const digest = await sha(JSON.stringify(body));
          const previous = await sql`SELECT actor,payload_hash,result FROM aproar_web_requests WHERE id=${body.requestId}`;
          if (previous.length) {
            if (previous[0].actor !== session.user || previous[0].payload_hash !== digest)
              return json({ error: "Identificador de requisi\xE7\xE3o reutilizado." }, 409);
            return json({ ok: true, requestId: body.requestId, replayed: true });
          }
          await applyCatalogRegistration(sql, body.requestId, session.user, digest, async () => {
            const rows = await sql`
        SELECT c.id::text AS id,c.colaborador_id::text AS colaborador_id,
               c.observacao,c.custos_separados,
               EXISTS(SELECT 1 FROM apontamentos a WHERE a.convocacao_id=c.id::text) AS has_point,
               EXISTS(SELECT 1 FROM servicos_apontamento s WHERE s.convocacao_id=c.id::text) AS has_services,
               EXISTS(SELECT 1 FROM conflitos_convocacao f WHERE f.convocacao_existente_id=c.id::text) AS has_conflict
        FROM convocacoes c WHERE c.id::text=${String(body.convocacaoId)} LIMIT 1`;
            const current = rows[0];
            if (!current) return Promise.reject(Object.assign(Error("Inclus\xE3o n\xE3o encontrada. Atualize a p\xE1gina e confira a equipe."), { status: 409 }));
            if (current.colaborador_id !== String(body.colaboradorId))
              throw Object.assign(Error("A inclus\xE3o selecionada n\xE3o corresponde ao colaborador. Atualize a p\xE1gina."), { status: 409 });
            const meta = metadata(current.observacao).meta;
            if (current.has_point || current.has_services || current.has_conflict || current.custos_separados === true || meta.apontado_em)
              throw Object.assign(Error("Este colaborador j\xE1 possui apontamento ou hist\xF3rico vinculado. A remo\xE7\xE3o autom\xE1tica foi bloqueada."), { status: 409 });
            return [
              { table: "convocacoes", action: "delete", id: String(body.convocacaoId) },
              { table: "auditoria", action: "insert", id: "audit:" + body.requestId, data: {
                entidade: "convocacoes",
                entidade_id: String(body.convocacaoId),
                acao: "REMOVER_INCLUSAO_SEM_APONTAMENTO",
                usuario: session.user,
                ocorrido_em: (/* @__PURE__ */ new Date()).toISOString(),
                contexto: { colaboradorId: String(body.colaboradorId), motivo: "Inclus\xE3o acidental corrigida na Controladoria" }
              } }
            ];
          });
          return json({ ok: true, requestId: body.requestId });
        }
        if (path === "/api/unpointed-convocation-remove" && request.method === "POST") {
          if (!["SUPERVISOR", "CONTROLADORIA"].includes(session.role)) return json({ error: "Acesso n\xE3o autorizado." }, 403);
          if (!sameOrigin(request)) return json({ error: "Origem n\xE3o autorizada." }, 403);
          if (!writes(env)) return json({ error: "Grava\xE7\xE3o indispon\xEDvel neste ambiente." }, 403);
          const body = await bodyJSON(request), id2 = String(body?.convocationId || ""), colaboradorId = String(body?.colaboradorId || "");
          if (!/^[0-9]+$/.test(id2) || !/^[0-9]+$/.test(colaboradorId) || !/^[a-f0-9-]{36}$/i.test(body?.requestId || ""))
            return json({ error: "Identificador de convoca\xE7\xE3o ou colaborador inv\xE1lido." }, 400);
          const digest = await sha(JSON.stringify(body));
          const previous = await sql`SELECT actor,payload_hash FROM aproar_web_requests WHERE id=${body.requestId}`;
          if (previous.length) {
            if (previous[0].actor !== session.user || previous[0].payload_hash !== digest) return json({ error: "Identificador reutilizado." }, 409);
            return json({ ok: true, requestId: body.requestId, replayed: true });
          }
          const rows = await sql`SELECT c.id,c.engenheiro,c.criado_por,c.colaborador_id,c.data,c.obra_id,
       EXISTS(SELECT 1 FROM apontamentos a WHERE a.convocacao_id=c.id::text) AS apontado,
       EXISTS(SELECT 1 FROM servicos_apontamento s WHERE s.convocacao_id=c.id::text) AS servicos,
       EXISTS(SELECT 1 FROM conflitos_convocacao k WHERE k.convocacao_existente_id=c.id::text) AS conflito
       FROM convocacoes c WHERE c.id=${id2}::bigint`;
          const conv = rows[0];
          if (!conv) return json({ error: "Inclus\xE3o n\xE3o encontrada. Atualize o apontamento." }, 404);
          if (String(conv.colaborador_id) !== colaboradorId) return json({ error: "A convoca\xE7\xE3o selecionada n\xE3o corresponde a este colaborador. Atualize os dados." }, 409);
          if (session.role === "SUPERVISOR" && conv.engenheiro !== session.user)
            return json({ error: "S\xF3 \xE9 poss\xEDvel retirar inclus\xF5es sem apontamento da sua pr\xF3pria equipe." }, 403);
          if (conv.apontado || conv.servicos || conv.conflito)
            return json({ error: "Este colaborador j\xE1 possui apontamento ou hist\xF3rico vinculado. A exclus\xE3o autom\xE1tica est\xE1 bloqueada; solicite confer\xEAncia \xE0 Controladoria." }, 409);
          const version = await sql`SELECT aproar_web_fingerprint() AS version`;
          const ops = [
            { table: "convocacoes", action: "delete", id: id2 },
            {
              table: "auditoria",
              action: "insert",
              id: "audit:" + body.requestId,
              data: {
                entidade: "aproar-web",
                entidade_id: id2,
                acao: "REMOVER_INCLUSAO_SEM_APONTAMENTO",
                usuario: session.user,
                ocorrido_em: (/* @__PURE__ */ new Date()).toISOString(),
                contexto: { convocacaoId: id2, colaboradorId, criadoPor: conv.criado_por, responsavel: conv.engenheiro }
              }
            }
          ];
          await sql`SELECT aproar_web_apply(${version[0].version},${body.requestId},${session.user},${digest},${JSON.stringify(ops)}::jsonb)`;
          return json({ ok: true, requestId: body.requestId });
        }
        if (path === "/api/admin-relocation" && request.method === "POST") {
          if (session.role !== "CONTROLADORIA") return json({ error: "Somente a Controladoria pode transferir convocados." }, 403);
          if (!sameOrigin(request)) return json({ error: "Origem n\xE3o autorizada." }, 403);
          if (!writes(env)) return json({ error: "Grava\xE7\xE3o n\xE3o autorizada na produ\xE7\xE3o." }, 403);
          const input = await bodyJSON(request), parsed = validateAdminRelocationInput(input);
          const digest = await sha(JSON.stringify(input));
          const previous = await sql`SELECT actor,payload_hash FROM aproar_web_requests WHERE id=${parsed.requestId}`;
          if (previous.length) {
            if (previous[0].actor !== session.user || previous[0].payload_hash !== digest)
              return json({ error: "Identificador da transfer\xEAncia reutilizado com dados diferentes." }, 409);
            return json({ ok: true, requestId: parsed.requestId, replayed: true });
          }
          await applyCatalogRegistration(sql, parsed.requestId, session.user, digest, async () => {
            const currentRows = await sql`
        SELECT c.id::text AS id,c.colaborador_id::text AS colaborador_id,
          c.data,c.turno,c.obra_id::text AS obra_id,c.engenheiro,c.observacao,c.custos_separados,
          w.unidade,
          EXISTS(SELECT 1 FROM apontamentos a WHERE a.convocacao_id=c.id::text) AS has_point,
          EXISTS(SELECT 1 FROM servicos_apontamento s WHERE s.convocacao_id=c.id::text) AS has_services
        FROM convocacoes c JOIN obras w ON w.id=c.obra_id
        WHERE c.id=${parsed.convocacaoId}::bigint LIMIT 1`;
            const works = await sql`SELECT id::text AS id,unidade,nome FROM obras
        WHERE unidade=${parsed.destination.unidade} ORDER BY id`;
            const conflicts = await sql`SELECT id::text AS id,turno,observacao FROM convocacoes
        WHERE id<>${parsed.convocacaoId}::bigint AND colaborador_id=${parsed.colaboradorId}::bigint
        AND data=${parsed.destination.dataServico}::date`;
            const unavailable = await sql`SELECT 1 FROM indisponibilidades
        WHERE colaborador_id=${parsed.colaboradorId} AND inicio<=${parsed.destination.dataServico}::date
          AND fim>=${parsed.destination.dataServico}::date AND ativo IS DISTINCT FROM false LIMIT 1`;
            return buildAdminRelocationOperations({
              current: currentRows[0],
              works,
              conflicts,
              unavailable: unavailable.length > 0,
              request: parsed,
              actor: session.user,
              timestamp: (/* @__PURE__ */ new Date()).toISOString()
            });
          });
          return json({ ok: true, requestId: parsed.requestId });
        }
        if (path === "/api/save" && request.method === "POST") {
          if (!sameOrigin(request)) return json({ error: "Origem n\xE3o autorizada." }, 403);
          if (!writes(env)) return json({ error: "Grava\xE7\xE3o desativada ou sem autoriza\xE7\xE3o espec\xEDfica para este ambiente." }, 403);
          const compactAck = request.headers.get("x-aproar-save-ack") === "1";
          const body = await bodyJSON(request);
          if (!/^[a-f0-9-]{36}$/i.test(body.requestId || "") || typeof body.version !== "string") return json({ error: "Identificador de requisi\xE7\xE3o inv\xE1lido." }, 400);
          const digest = await sha(JSON.stringify(body)), previous = await sql`SELECT actor,payload_hash FROM aproar_web_requests WHERE id=${body.requestId}`;
          if (previous.length) {
            if (previous[0].actor !== session.user || previous[0].payload_hash !== digest) return json({ error: "Identificador de requisi\xE7\xE3o reutilizado." }, 409);
            return compactAck ? json({ ok: true, requestId: body.requestId, replayed: true }) : json({ ...summary(await readDatabase(sql, readOptions), session, env), ok: true, replayed: true });
          }
          const db = await readDatabase(sql, readOptions);
          if (body.version !== db.version) return json({ error: "Outro usu\xE1rio atualizou os dados. Suas altera\xE7\xF5es n\xE3o foram gravadas; recarregue e confira os registros." }, 409);
          if (session.role === "SUPERVISOR") {
            db.releaseEvents = await sql`SELECT acao,usuario,ocorrido_em,contexto FROM auditoria
       WHERE acao IN ('SOLICITACAO_LIBERACAO_FINANCEIRA','LIBERACAO_FINANCEIRA_AUTORIZADA',
         'LIBERACAO_FINANCEIRA_NEGADA','LIBERACAO_FINANCEIRA_UTILIZADA')
         AND contexto->>'supervisor'=${session.user} ORDER BY id ASC LIMIT 20000`;
          }
          const operations = buildOperations(db, body.state, session);
          if (!permittedProductionDeletion(env, session, db, operations)) {
            const denied = operations.filter((op) => op.action === "delete");
            const types = [...new Set(denied.map((op) => op.table))];
            console.warn("APROAR blocked unsafe removal", JSON.stringify({ role: session.role, types, count: denied.length }));
            return json({
              error: session.role === "SUPERVISOR" ? "N\xE3o foi poss\xEDvel salvar porque a altera\xE7\xE3o continha uma exclus\xE3o n\xE3o autorizada (" + types.join(", ") + "). Nenhum apontamento, convoca\xE7\xE3o ou registro financeiro foi apagado. Atualize a p\xE1gina e confira os servi\xE7os selecionados." : "A Controladoria s\xF3 pode excluir uma convoca\xE7\xE3o sem apontamento por vez ou at\xE9 50 obras sem v\xEDnculos. Corre\xE7\xF5es de servi\xE7os exigem auditoria. Registros com hist\xF3rico s\xE3o protegidos.",
              code: "APROAR_PROTECTED_REMOVAL",
              types
            }, 403);
          }
          operations.sort((a2, b2) => (a2.table === "obras" && a2.action === "delete" ? 1 : 0) - (b2.table === "obras" && b2.action === "delete" ? 1 : 0));
          if (operations.length) await sql`SELECT aproar_web_apply(${body.version},${body.requestId},${session.user},${digest},${JSON.stringify(operations)}::jsonb)`;
          return compactAck ? json({ ok: true, requestId: body.requestId }) : json({ ...summary(await readDatabase(sql, readOptions), session, env), ok: true });
        }
        return json({ error: "Rota n\xE3o encontrada." }, 404);
      }
      if (request.method !== "GET" && request.method !== "HEAD") return json({ error: "M\xE9todo n\xE3o permitido." }, 405);
      if (env.ASSETS) {
        const response = await env.ASSETS.fetch(request);
        const headers = new Headers(response.headers);
        for (const [k, v2] of Object.entries(common)) headers.set(k, v2);
        headers.set("content-security-policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'");
        return new Response(response.body, { status: response.status, headers });
      }
      return json({ message: "Interface ainda n\xE3o publicada." }, 404);
    } catch (e) {
      if (neonQuotaExceeded(e)) {
        console.error("APROAR Neon monthly quota reached", JSON.stringify({ route: path, code: "NEON_QUOTA_EXCEEDED", role: session?.role || "unknown" }));
        return json({ error: neonQuotaPublicMessage, code: "NEON_QUOTA_EXCEEDED" }, 503);
      }
      if (path === "/api/login") {
        console.error("APROAR login failure", JSON.stringify({ stage: loginStage, type: String(e?.name || "Error").slice(0, 60), code: String(e?.code || "none").slice(0, 60), status: Number(e?.status || 0) }));
        if (e.status) return json({ error: e.message, ...e.details ? { details: e.details } : {} }, e.status);
        return json({ error: "Falha interna no login. Etapa: " + loginStage + ". Consulte o registro do Worker." }, 502);
      }
      if (path.startsWith("/api/trello/")) {
        console.error("APROAR Trello route failure", JSON.stringify({
          route: path,
          type: String(e?.name || "Error").slice(0, 80),
          code: String(e?.code || "none").slice(0, 80),
          detail: String(e?.message || "No error message").slice(0, 320)
        }));
      }
      if (path === "/api/save") console.error("APROAR save rejected", JSON.stringify({
        code: String(e?.code || "unknown").slice(0, 32),
        name: String(e?.name || "Error").slice(0, 60),
        reason: String(e?.message || "").slice(0, 320),
        actorRole: session?.role || "unknown",
        route: path
      }));
      if (e.status) return json({ error: e.message, ...e.details ? { details: e.details } : {} }, e.status);
      const message = String(e.message || "");
      if (message.includes("APROAR_CONFLITO_TURNO")) return json({ error: "H\xE1 outra convoca\xE7\xE3o no mesmo turno para um dos colaboradores. Confira a data antes de regularizar o apontamento." }, 409);
      if (e.code === "57014" || e.code === "55P03") return json({ error: "O banco est\xE1 ocupado ou excedeu o tempo permitido. Confira o hist\xF3rico antes de tentar novamente." }, 503);
      if (message.includes("APROAR_STALE")) return json({ error: "Os dados mudaram durante a grava\xE7\xE3o. Nenhuma altera\xE7\xE3o foi salva. Atualize e tente novamente." }, 409);
      if (message.includes("APROAR_REQUEST_MISMATCH")) return json({ error: "Requisi\xE7\xE3o repetida com conte\xFAdo diferente." }, 409);
      if (e.code === "23505") {
        const constraint = String(e?.constraint || e?.constraint_name || "").slice(0, 90);
        console.error("APROAR unique conflict", JSON.stringify({ route: path, role: session?.role || "unknown", constraint }));
        if (constraint === "ux_colaboradores_nome_upper")
          return json({ error: "Este nome j\xE1 est\xE1 cadastrado. No retroativo, selecione o colaborador existente; n\xE3o insira outro avulso com o mesmo nome. Seu rascunho foi preservado." }, 409);
        if (constraint === "apontamentos_convocacao_id_key")
          return json({ error: "Esta convoca\xE7\xE3o j\xE1 possui um apontamento registrado. Abra o apontamento existente para conferir ou corrigir; o sistema n\xE3o deve duplicar a presen\xE7a." }, 409);
        if (constraint === "uq_conflito_pendente_equivalente")
          return json({ error: "Este conflito entre convoca\xE7\xF5es j\xE1 est\xE1 registrado. Confira as equipes e turnos existentes antes de tentar novamente." }, 409);
        return json({ error: "O Neon bloqueou a grava\xE7\xE3o por registro duplicado. Nenhum segundo registro foi criado. Confira a data, a equipe e os avulsos cadastrados antes de salvar novamente." }, 409);
      }
      if (e.code === "23503") return json({ error: "Este registro est\xE1 vinculado ao hist\xF3rico e n\xE3o pode ser exclu\xEDdo." }, 409);
      if (e.code === "42883" || e.code === "42P01") return json({ error: "Estrutura do banco incompleta: confira a migra\xE7\xE3o de banco correspondente ao ambiente." }, 503);
      if (path === "/api/save") {
        const diagnosis = /^[0-9A-Z]{5}$/.test(String(e?.code || "")) ? String(e.code) : "INDEFINIDO";
        return json({ error: "O banco n\xE3o confirmou o salvamento. Refer\xEAncia t\xE9cnica DB-" + diagnosis + ". O formul\xE1rio foi preservado: confira as pend\xEAncias antes de tentar novamente." }, 502);
      }
      return json({ error: "N\xE3o foi poss\xEDvel concluir a opera\xE7\xE3o. Confira a conex\xE3o e a estrutura do banco." }, 502);
    }
  },
  async scheduled(event, env, ctx) {
    if (env.TRELLO_AUTO_SYNC_ENABLED !== "true" || !writes(env)) return;
    ctx.waitUntil((async () => {
      try {
        const sql = ys(env.DATABASE_URL);
        const r = await sql`SELECT sincronizado_obras_em,ultima_tentativa_obras_em FROM trello_snapshot WHERE snapshot_id=1`;
        const last = r[0]?.sincronizado_obras_em || r[0]?.ultima_tentativa_obras_em;
        if (last && Date.now() - new Date(last).getTime() < 11.5 * 60 * 60 * 1e3) return;
        await sincronizarTrello(sql);
      } catch (e) {
        console.error("Falha na sincroniza\xE7\xE3o Trello:", String(e?.message || e));
      }
    })());
  }
};
export {
  worker_default as default
};
/*! Bundled license information:

@neondatabase/serverless/index.mjs:
  (*! Bundled license information:
  
  ieee754/index.js:
    (*! ieee754. BSD-3-Clause License. Feross Aboukhadijeh <https://feross.org/opensource> *)
  
  buffer/index.js:
    (*!
     * The buffer module from node.js, for the browser.
     *
     * @author   Feross Aboukhadijeh <https://feross.org>
     * @license  MIT
     *)
  *)
*/
//# sourceMappingURL=worker.js.map