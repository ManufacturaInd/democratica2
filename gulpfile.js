var gulp = require('gulp');
var sass = require('gulp-sass');
var connect = require('gulp-connect');
var wiredep = require('wiredep').stream;

gulp.task('connect', function(){
  connect.server({
    root: 'public',
    livereload: true
  });
});

gulp.task('sass', function () {
  return gulp.src('assets/sass/**/*.scss')
      .pipe(sass({ 
        errLogToConsole: true,
        sourceComments: true,
        includePaths: ['bower_components/foundation/scss']
      }).on('error', sass.logError))
      .pipe(gulp.dest('dist/assets/css'));
});

gulp.task('fonts', function () {
  return gulp.src('assets/fonts/**/*.*')
      .pipe(gulp.dest('dist/assets/fonts'));
});

gulp.task('img', function () {
  return gulp.src('assets/img/**/*.*')
      .pipe(gulp.dest('dist/assets/img'));
});

gulp.task('scripts', function () {
  return gulp.src('assets/scripts/**/*.js')
      .pipe(gulp.dest('dist/assets/scripts'));
});


gulp.task('livereload', function (){
  return gulp.src('./public/**/*')
  .pipe(connect.reload());
});

gulp.task('watch', function () {
  gulp.watch('assets/sass/**/*.scss', ['sass']);
  gulp.watch('assets/img/**/*.*', ['img']);
  gulp.watch('assets/scripts/*.js', ['scripts']);
  gulp.watch('dist/**/**/*', ['livereload']);
});

// Inject Bower components
gulp.task('wiredep', function () {
    gulp.src('assets/sass/*.scss')
        .pipe(wiredep({
            directory: 'bower_components',
            ignorePath: 'bower_components/'
        }))
        .pipe(gulp.dest('assets/sass'));
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

gulp.task('build', ['sass', 'fonts', 'img', 'scripts']);
gulp.task('default', ['sass', 'fonts', 'img', 'scripts', 'connect', 'watch']);

