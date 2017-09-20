/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};

/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {

/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId])
/******/ 			return installedModules[moduleId].exports;

/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			exports: {},
/******/ 			id: moduleId,
/******/ 			loaded: false
/******/ 		};

/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);

/******/ 		// Flag the module as loaded
/******/ 		module.loaded = true;

/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}


/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;

/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;

/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";

/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(0);
/******/ })
/************************************************************************/
/******/ ([
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	"use strict";

	//var _markupMenu = __webpack_require__(1);

	var _filter = __webpack_require__(3);

	var _filter2 = _interopRequireDefault(_filter);

	var _mobileFilter = __webpack_require__(4);

	var _mobileFilter2 = _interopRequireDefault(_mobileFilter);

	function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

	//(0, _markupMenu.markupMenu)(window.document);

	$(function () {
	  (0, _filter2.default)();
	  // (0, _mobileFilter2.default)();
	});

/***/ },
/* 1 */
/***/ function(module, exports, __webpack_require__) {

	'use strict';

	Object.defineProperty(exports, "__esModule", {
	  value: true
	});
	exports.markupMenu = markupMenu;

	var _files = __webpack_require__(2);

	var _files2 = _interopRequireDefault(_files);

	function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

	function markupMenu(document) {
	  var nav = document.createElement('div');
	  var style = document.createElement('style');
	  var button = document.createElement('button');
	  var wrapper = document.createElement('div');
	  wrapper.appendChild(button);
	  wrapper.appendChild(nav);
	  wrapper.className = 'helper-nav-wrapper';
	  button.innerHTML = "Open pages list";
	  button.className = 'helper-nav-button';
	  nav.className = 'helper-nav';
	  style.innerHTML = '.helper-nav a:hover {\n      color:#fff;\n      background-color:#000;\n    }\n    .helper-nav a {\n      display:block;\n      color: #000;\n      padding: 3px;\n      margin:0\n    }\n    .helper-nav-button {\n      background: #000;\n      color: #fff;\n      padding: 5px;\n    }\n    .helper-nav-wrapper {\n      position: fixed;\n      bottom: 0;\n      right: 0;\n      font-family: monospace;\n      z-index: 9999;\n      text-align: right;\n      font-size: 14px;\n    }\n    .helper-nav {\n      text-align: left;\n      background-color: #fff;\n      border: 1px solid #000;\n      padding: 3px;\n      boxShadow: 0 0 40px 0 rgba(0,0,0,.2);\n      max-height: 300px;\n      overflow-y: auto;\n    }\n    @media all and (max-width:1024px) {\n      .helper-nav {\n        height: 160px;\n        overflow-y: scroll;\n      }\n    }';
	  document.head.appendChild(style);
	  if (_files2.default[0] !== 'dev') {
	    console.warn('Art Lemon production');
	    return;
	  }
	  for (var i = 1; i < _files2.default.length; i++) {
	    nav.innerHTML += '<a href=' + _files2.default[i] + '"/">' + i + '-' + _files2.default[i] + '</a>';
	  }
	  document.body.appendChild(wrapper);
	  var flag = localStorage.getItem('flag') ? JSON.parse(localStorage.getItem('flag')) : false;
	  var display = flag ? 'block' : 'none';
	  var btnText = flag ? 'Close pages list' : 'Open pages list';
	  nav.style.display = display;
	  button.innerHTML = btnText;

	  function toggleNav() {
	    if (flag) {
	      nav.style.display = 'none';
	      button.innerHTML = 'Open pages list';
	    } else {
	      nav.style.display = 'block';
	      button.innerHTML = 'Close pages list';
	    }
	    flag = !flag;
	    localStorage.setItem('flag', flag);
	  }
	  document.addEventListener('keyup', function (e) {
	    if (e.type === 'keyup' && e.ctrlKey && e.keyCode === 88) {
	      toggleNav();
	    }
	  });
	  button.addEventListener('click', toggleNav);
	}

/***/ },
/* 2 */
/***/ function(module, exports) {

	"use strict";

	Object.defineProperty(exports, "__esModule", {
	  value: true
	});
	exports.default = ["dev", "index.html", "product.html" , "login.html" , "person-cab_ads.html" , "person-cab_massage.html" , "dialog.html" , "settings.html" , "person-cab_favorites.html" , "create-ads.html" , "about.html" , "blog.html" , "faq.html" , "one-news.html" , "user-page.html" , "specification.html"];

/***/ },
/* 3 */
/***/ function(module, exports) {

	'use strict';

	Object.defineProperty(exports, "__esModule", {
	  value: true
	});
	var filter = function filter() {

	  $('.header__filter').on('click', function (e) {
	    e.stopPropagation();
	    $('.filter').addClass('visible');
	  });
	  $('.filter').on('click', function (e) {
	    e.stopPropagation();
	  });
	  $('.wrapper').on('click', function () {
	    $('.filter').removeClass('visible');
	  });

	  jcf.setOptions('Select', {
	    wrapNative: false,
	    flipDropToFit: false,
	    maxVisibleItems: 5
	  });
	  jcf.replaceAll();
	  $('.filter__reset').on('click', function () {
	    $('.filter input').val('');
	    $('.filter__option').prop('selected', function () {
	      return this.defaultSelected;
	    });
	    jcf.replaceAll();
	  });
	  $('.filter__value').keydown(function (event) {
	    if (event.keyCode == 46 || event.keyCode == 8 || event.keyCode == 9 || event.keyCode == 27 || event.keyCode == 65 && event.ctrlKey === true || event.keyCode >= 35 && event.keyCode <= 39) {
	      return;
	    } else {
	      if ((event.keyCode < 48 || event.keyCode > 57) && (event.keyCode < 96 || event.keyCode > 105)) {
	        event.preventDefault();
	      }
	    }
	  });
	};
	exports.default = filter;

/***/ },
/* 4 */
/***/ function(module, exports) {

	'use strict';

	Object.defineProperty(exports, "__esModule", {
	  value: true
	});
	// var mobileFilter = function mobileFilter() {
	//   if ($(window).innerWidth() <= 1200) {
	//     $('.filter__form-filter').find('.filter__row').eq(0).append($('.filter__reset'));
	//   }
	//   if ($(window).innerWidth() <= 960) {
	//     $('.filter__form-filter').find('.filter__row').eq(1).append($('.filter__reset'));
	//   }
	//   $('.filter__open').on('click', function () {
	//     $('.filter__form-filter').addClass('visible');
	//     $('body, html').addClass('hidden');
	//   });
	//   $('.filter__close').on('click', function () {
	//     $('.filter__form-filter').removeClass('visible');
	//     $('body, html').removeClass('hidden');
	//   });
	// };
	// exports.default = mobileFilter;

/***/ }
/******/ ]);
//# sourceMappingURL=application.js.mapn.js.map


// tabs

(function($){				
	jQuery.fn.lightTabs = function(options){

		var createTabs = function(){
			tabs = this;
			i = 0;
				showPage = function(i){
					$(tabs).children(".tabs-items-log").children("div").hide().removeClass("active");
					$(tabs).children(".tabs-items-log").children("div").eq(i).addClass("active").show();
					$(tabs).children(".tabs-title-log").children("a").removeClass("active");
					$(tabs).children(".tabs-title-log").children("a").eq(i).addClass("active");
				}
								
			showPage(0);				
			
			$(tabs).children(".tabs-title-log").children("a").each(function(index, element){
				$(element).attr("data-page", i);
				i++;                     
			});
			
			$(tabs).children(".tabs-title-log").children("a").click(function(){
				showPage(parseInt($(this).attr("data-page")));
				setTimeout(function() {jcf.replaceAll();}, 100);
			});				
		};		
		return this.each(createTabs);
	};

	// tabs
	$(".tabs-log").lightTabs();
	// tabs

	// addition-click
	$(".addition-title").on("click" , function() {
		$(this).toggleClass("active");
		$(".addition-box").slideToggle();
	});
	// addition-click

	$(".hint-info_box .close-btn").on("click" , function() {
		$(this).parent().removeClass("show");
	});


	$(".model-window,.popup .close-btn").on( "click" , function(event){
        event.stopPropagation();
        $(".model-window").fadeOut(200);
    });

	$(".popup-hint-info,.popup-user_message").on("click", function(event){
        event.stopPropagation();
    });

    $(".btn-write").on("click", function(event){
        $("#model-user_message").fadeIn(200);
    });
	
})(jQuery);
