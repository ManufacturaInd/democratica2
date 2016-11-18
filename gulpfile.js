var gulp = require('gulp');
var sass = require('gulp-sass');
var connect = require('gulp-connect');

gulp.task('connect', function(){
  connect.server({
    root: 'public',
    livereload: true
  });
});

gulp.task('sass', function () {
  return gulp.src('./assets/sass/**/*.scss')
      .pipe(sass({ 
        errLogToConsole: true,
        sourceComments: true,
        includePaths: ['bower_components/foundation/scss']
      }).on('error', sass.logError))
      .pipe(gulp.dest('./public/assets/css'));
});

gulp.task('fonts', function () {
  return gulp.src('./assets/fonts/**/*.*')
      .pipe(gulp.dest('./public/assets/fonts'));
});

gulp.task('img', function () {
  return gulp.src('./assets/img/**/*.*')
      .pipe(gulp.dest('./public/assets/img'));
});

gulp.task('scripts', function () {
  return gulp.src('./assets/scripts/**/*.js')
      .pipe(gulp.dest('./public/assets/scripts'));
});

gulp.task('livereload', function (){
  return gulp.src('./public/**/*')
  .pipe(connect.reload());
});

gulp.task('watch', function () {
  gulp.watch('./assets/sass/**/*.scss', ['sass']);
  gulp.watch('./assets/img/**/*.*', ['img']);
  gulp.watch('./assets/scripts/*.js', ['scripts']);
  gulp.watch('./public/**/**/*', ['livereload']);
});

gulp.task('build', ['sass', 'fonts', 'img', 'scripts']);
gulp.task('default', ['sass', 'fonts', 'img', 'scripts', 'connect', 'watch']);

