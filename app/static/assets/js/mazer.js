(() => {
  var e,
    t = {
      750: () => {
        function e(e, t) {
          if (!(e instanceof t))
            throw new TypeError("Cannot call a class as a function");
        }
        function t(e, t) {
          for (var i = 0; i < t.length; i++) {
            var o = t[i];
            (o.enumerable = o.enumerable || !1),
              (o.configurable = !0),
              "value" in o && (o.writable = !0),
              Object.defineProperty(e, o.key, o);
          }
        }
        function i(e, t, i, o) {
          void 0 === t && (t = 400),
            void 0 === o && (o = !1),
            (e.style.overflow = "hidden"),
            o && (e.style.display = "block");
          var r,
            n = window.getComputedStyle(e),
            a = parseFloat(n.getPropertyValue("height")),
            s = parseFloat(n.getPropertyValue("padding-top")),
            l = parseFloat(n.getPropertyValue("padding-bottom")),
            d = parseFloat(n.getPropertyValue("margin-top")),
            c = parseFloat(n.getPropertyValue("margin-bottom")),
            u = a / t,
            v = s / t,
            p = l / t,
            y = d / t,
            h = c / t;
          window.requestAnimationFrame(function n(f) {
            void 0 === r && (r = f);
            var g = f - r;
            o
              ? ((e.style.height = u * g + "px"),
                (e.style.paddingTop = v * g + "px"),
                (e.style.paddingBottom = p * g + "px"),
                (e.style.marginTop = y * g + "px"),
                (e.style.marginBottom = h * g + "px"))
              : ((e.style.height = a - u * g + "px"),
                (e.style.paddingTop = s - v * g + "px"),
                (e.style.paddingBottom = l - p * g + "px"),
                (e.style.marginTop = d - y * g + "px"),
                (e.style.marginBottom = c - h * g + "px")),
              g >= t
                ? ((e.style.height = ""),
                  (e.style.paddingTop = ""),
                  (e.style.paddingBottom = ""),
                  (e.style.marginTop = ""),
                  (e.style.marginBottom = ""),
                  (e.style.overflow = ""),
                  o || (e.style.display = "none"),
                  "function" == typeof i && i())
                : window.requestAnimationFrame(n);
          });
        }
        var o = (function () {
            function o(t) {
              var i =
                arguments.length > 1 && void 0 !== arguments[1]
                  ? arguments[1]
                  : {};
              e(this, o),
                (this.sidebarEL =
                  t instanceof HTMLElement ? t : document.querySelector(t)),
                (this.options = i),
                this.init();
            }
            var r, n, a;
            return (
              (r = o),
              (n = [
                {
                  key: "init",
                  value: function () {
                    var e = this;
                    document
                      .querySelectorAll(".burger-btn")
                      .forEach(function (t) {
                        return t.addEventListener("click", e.toggle.bind(e));
                      }),
                      document
                        .querySelectorAll(".sidebar-hide")
                        .forEach(function (t) {
                          return t.addEventListener("click", e.toggle.bind(e));
                        }),
                      window.addEventListener(
                        "resize",
                        this.onResize.bind(this)
                      );
                    for (
                      var t = document.querySelectorAll(
                          ".sidebar-item.has-sub"
                        ),
                        o = function () {
                          var e = t[r];
                          t[r]
                            .querySelector(".sidebar-link")
                            .addEventListener("click", function (t) {
                              t.preventDefault();
                              var o = e.querySelector(".submenu");
                              o.classList.contains("active") &&
                                (o.style.display = "block"),
                                "none" == o.style.display
                                  ? o.classList.add("active")
                                  : o.classList.remove("active"),
                                (function (e, t, o) {
                                  0 === e.clientHeight
                                    ? i(e, t, o, !0)
                                    : i(e, t, o);
                                })(o, 300);
                            });
                        },
                        r = 0;
                      r < t.length;
                      r++
                    )
                      o();
                    if ("function" == typeof PerfectScrollbar) {
                      var n = document.querySelector(".sidebar-wrapper");
                      new PerfectScrollbar(n, { wheelPropagation: !1 });
                    }
                    setTimeout(function () {
                      return document.querySelector(".sidebar-item.active");
                    }, 100),
                      this.onFirstLoad();
                  },
                },
                {
                  key: "onFirstLoad",
                  value: function () {
                    window.innerWidth < 1200 &&
                      this.sidebarEL.classList.remove("active");
                  },
                },
                {
                  key: "onResize",
                  value: function () {
                    window.innerWidth < 1200
                      ? this.sidebarEL.classList.remove("active")
                      : this.sidebarEL.classList.add("active"),
                      this.deleteBackdrop(),
                      this.toggleOverflowBody(!0);
                  },
                },
                {
                  key: "toggle",
                  value: function () {
                    this.sidebarEL.classList.contains("active")
                      ? this.hide()
                      : this.show();
                  },
                },
                {
                  key: "show",
                  value: function () {
                    this.sidebarEL.classList.add("active"),
                      this.createBackdrop(),
                      this.toggleOverflowBody();
                  },
                },
                {
                  key: "hide",
                  value: function () {
                    this.sidebarEL.classList.remove("active"),
                      this.deleteBackdrop(),
                      this.toggleOverflowBody();
                  },
                },
                {
                  key: "createBackdrop",
                  value: function () {
                    this.deleteBackdrop();
                    var e = document.createElement("div");
                    e.classList.add("sidebar-backdrop"),
                      e.addEventListener("click", this.hide.bind(this)),
                      document.body.appendChild(e);
                  },
                },
                {
                  key: "deleteBackdrop",
                  value: function () {
                    var e = document.querySelector(".sidebar-backdrop");
                    e && e.remove();
                  },
                },
                {
                  key: "toggleOverflowBody",
                  value: function (e) {
                    var t = this.sidebarEL.classList.contains("active"),
                      i = document.querySelector("body");
                    i.style.overflowY =
                      void 0 === e
                        ? t
                          ? "hidden"
                          : "auto"
                        : e
                        ? "auto"
                        : "hidden";
                  },
                },
              ]) && t(r.prototype, n),
              a && t(r, a),
              o
            );
          })(),
          r = document.getElementById("sidebar");
        r && (window.sidebar = new o(r));
      },
      797: (e, t, i) => {
        "use strict";
        i(750);
      },
      298: () => {},
      236: () => {},
      212: () => {},
      447: () => {},
      329: () => {},
      881: () => {},
      386: () => {},
      147: () => {},
    },
    i = {};
  function o(e) {
    var r = i[e];
    if (void 0 !== r) return r.exports;
    var n = (i[e] = { exports: {} });
    return t[e](n, n.exports, o), n.exports;
  }
  (o.m = t),
    (e = []),
    (o.O = (t, i, r, n) => {
      if (!i) {
        var a = 1 / 0;
        for (d = 0; d < e.length; d++) {
          for (var [i, r, n] = e[d], s = !0, l = 0; l < i.length; l++)
            (!1 & n || a >= n) && Object.keys(o.O).every((e) => o.O[e](i[l]))
              ? i.splice(l--, 1)
              : ((s = !1), n < a && (a = n));
          s && (e.splice(d--, 1), (t = r()));
        }
        return t;
      }
      n = n || 0;
      for (var d = e.length; d > 0 && e[d - 1][2] > n; d--) e[d] = e[d - 1];
      e[d] = [i, r, n];
    }),
    (o.n = (e) => {
      var t = e && e.__esModule ? () => e.default : () => e;
      return o.d(t, { a: t }), t;
    }),
    (o.d = (e, t) => {
      for (var i in t)
        o.o(t, i) &&
          !o.o(e, i) &&
          Object.defineProperty(e, i, { enumerable: !0, get: t[i] });
    }),
    (o.o = (e, t) => Object.prototype.hasOwnProperty.call(e, t)),
    (() => {
      var e = {
        254: 0,
        12: 0,
        348: 0,
        37: 0,
        673: 0,
        464: 0,
        770: 0,
        376: 0,
        825: 0,
      };
      o.O.j = (t) => 0 === e[t];
      var t = (t, i) => {
          var r,
            n,
            [a, s, l] = i,
            d = 0;
          for (r in s) o.o(s, r) && (o.m[r] = s[r]);
          if (l) var c = l(o);
          for (t && t(i); d < a.length; d++)
            (n = a[d]), o.o(e, n) && e[n] && e[n][0](), (e[a[d]] = 0);
          return o.O(c);
        },
        i = (self.webpackChunkmazer = self.webpackChunkmazer || []);
      i.forEach(t.bind(null, 0)), (i.push = t.bind(null, i.push.bind(i)));
    })(),
    o.O(void 0, [12, 348, 37, 673, 464, 770, 376, 825], () => o(797)),
    o.O(void 0, [12, 348, 37, 673, 464, 770, 376, 825], () => o(447)),
    o.O(void 0, [12, 348, 37, 673, 464, 770, 376, 825], () => o(329)),
    o.O(void 0, [12, 348, 37, 673, 464, 770, 376, 825], () => o(881)),
    o.O(void 0, [12, 348, 37, 673, 464, 770, 376, 825], () => o(386)),
    o.O(void 0, [12, 348, 37, 673, 464, 770, 376, 825], () => o(147)),
    o.O(void 0, [12, 348, 37, 673, 464, 770, 376, 825], () => o(298)),
    o.O(void 0, [12, 348, 37, 673, 464, 770, 376, 825], () => o(236));
  var r = o.O(void 0, [12, 348, 37, 673, 464, 770, 376, 825], () => o(212));
  r = o.O(r);
})();
