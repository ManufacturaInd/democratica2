var gulp = require('gulp');
var sass = require('gulp-sass');
var connect = require('gulp-connect');
var cleanCSS = require('gulp-clean-css');
var wiredep = require('wiredep').stream;
var mainBowerFiles = require('gulp-main-bower-files');
var debug = require('gulp-debug');

gulp.task('connect', function(){
  connect.server({
    root: 'public',
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
      .pipe(gulp.dest('dist/assets/css'));
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

gulp.task('livereload', function (){
  return gulp.src('./public/**/*')
  .pipe(connect.reload());
});

gulp.task('watch', function () {
  gulp.watch('assets/sass/**/*.scss', ['styles']);
  // gulp.watch('assets/img/**/*.*', ['img']);
  // gulp.watch('assets/scripts/**/*.js', ['scripts']);
  // gulp.watch('dist/**/**/*', ['livereload']);
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

gulp.task('build', ['styles', 'fonts', 'img', 'scripts', 'bowerfiles']);
gulp.task('default', ['styles', 'fonts', 'img', 'scripts', 'bowerfiles', 'connect', 'watch']);

