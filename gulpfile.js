var gulp = require('gulp');
var sass = require('gulp-sass');
var connect = require('gulp-connect');
var cleanCSS = require('gulp-clean-css');
var wiredep = require('wiredep').stream;
var mainBowerFiles = require('gulp-main-bower-files');
var debug = require('gulp-debug');
var exec = require('child_process').exec;

// use python scripts to generate HTML from templates
// the "--render" option is what determines which pages are generated
// see https://nodejs.org/api/child_process.html#child_process_child_process_execsync_command_options
var cmd = ". .env/bin/activate && python site-generator/generate.py --fast-run --render ";

gulp.task('html-index',         function(cb) { exec(cmd + 'homepage', function(e) { cb(e); }); });
gulp.task('html-mp-index',      function(cb) { exec(cmd + 'mp_index', function(e) { cb(e); }); });
gulp.task('html-mp-pages',      function(cb) { exec(cmd + 'mp_pages', function(e) { cb(e); }); });
gulp.task('html-session-index', function(cb) { exec(cmd + 'session_index', function(e) { cb(e); }); });
gulp.task('html-session-pages', function(cb) { exec(cmd + 'session_pages', function(e) { cb(e); }); });
gulp.task('html',               function(cb) { exec(cmd + 'all', function(e) { cb(e); }); });

gulp.task('connect', function(){
  connect.server({
    root: 'dist',
    livereload: true
  });
});

gulp.task('styles', function () {
  return gulp.src('assets/sass/**/*.scss')
      .pipe(sass({ 
        errLogToConsole: true,
        sourceComments: true,
        includePaths: ['bower_components/foundation-sites/scss']
      }).on('error', sass.logError))
      .pipe(cleanCSS({compatibility: 'ie8'}))
      .pipe(gulp.dest('dist/assets/css'))
      .pipe(connect.reload());
});

gulp.task('scripts', function () {
  return gulp.src('assets/scripts/**/*.js')
      .pipe(gulp.dest('dist/assets/scripts'));
});

gulp.task('img', function () {
  return gulp.src('assets/img/**/*.*')
      .pipe(gulp.dest('dist/assets/img'));
});

gulp.task('fonts', function () {
  return gulp.src('assets/fonts/**/*.*')
      .pipe(gulp.dest('dist/assets/fonts'));
});

gulp.task('bowerfiles', function(){
  return gulp.src('./bower.json')
    .pipe(mainBowerFiles( ))
    //.pipe(uglify())
    .pipe(gulp.dest('dist/bower_components'));
});

gulp.task('watch', ['connect'], function () {
  gulp.watch('assets/sass/**/*.scss', ['styles']);
  // img/ has lots of MP images, therefore eats up lots of time re-watching
  // so we're not watching it ATM
  // gulp.watch('assets/img/**/*.*', ['img']);

  gulp.watch('templates/base.html',                 ['html']);
  gulp.watch('templates/index.html',                ['html-index']);
  gulp.watch('templates/mp_list.html',              ['html-mp-index']);
  gulp.watch('templates/mp_detail.html',            ['html-mp-pages']);
  gulp.watch('templates/session_list.html',         ['html-session-index']);
  gulp.watch(['templates/session_detail.html',
    'templates/snippets-session/*.html'], ['html-session-pages']);
  gulp.watch(['dist/index.html', 
              'dist/deputados/index.html', 
              'dist/deputados/zita-seabra/index.html', 
              'dist/sessoes/2016/10/26/index.html'], 
    function(file) {
      // reload browser on HTML file changes
      gulp.src(file.path).pipe(connect.reload());
    });
});

// Inject Bower components
gulp.task('wiredep', function () {
    gulp.src('assets/sass/*.scss')
        .pipe(wiredep({
            directory: 'bower_components',
            ignorePath: 'bower_components/'
        }))
        .pipe(gulp.dest('assets/css'));
    gulp.src('assets/scripts/*.js')
        .pipe(wiredep({
            directory: 'bower_components',
            ignorePath: 'bower_components/'
        }))
        .pipe(gulp.dest('assets/scripts'));
    gulp.src('templates/**/*.html')
        .pipe(wiredep({
            directory: 'bower_components',
            ignorePath: 'templates/'
        }))
        .pipe(gulp.dest('templates'));
});

gulp.task('build', ['html', 'styles', 'fonts', 'img', 'scripts', 'bowerfiles']);
gulp.task('default', ['html', 'styles', 'fonts', 'img', 'scripts', 'bowerfiles', 'connect', 'watch']);

