/*
Language: dialog description language
Author: Mark Birger <birgerm@yandex.ru>
Category: common
*/

hljs.registerLanguage("dlg", function(hljs) {

  var LINE_SETTER = {
    className: 'setter',
    begin: '^\t*\`', end: '\`[ \t]*\n',
  };
  var SETTER = {
    className: 'setter',
    begin: '\`', end: '\`'
  };
  var COMMENT = {
    className: 'comment',
    begin: '#', end: '\n'
  };
  var ANSWER = {
    className: 'answer',
    begin: '(\n|^)\t(\t\t)*((?=(\`|\'\"))|[^\t])', end: '\n',
    contains: [
      SETTER
    ]
  };
  var QUESTION = {
    className: 'question',
    begin: '(\n|^)(\t\t)*((?=(\`|\'\"))|[^\t])', end: '\n',
    contains: [
      SETTER
    ]
  };
  var LINE = {
    begin: '', end: '(\n|$)',
    contains: [
      LINE_SETTER,
      ANSWER,
      QUESTION,
      COMMENT
    ]
  }
  return {
    case_insensitive: true,
    contains: [
      LINE
    ]
  };
});