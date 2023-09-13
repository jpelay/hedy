const { defineConfig } = require("cypress");

module.exports = defineConfig({
  projectId: 'a1fbb9',
  watchForFileChanges: false,
  video: false,
  redirectionLimit: 100,
  e2e: {
    baseUrl: 'http://localhost:8080',
    setupNodeEvents(on, config) {
      require('@cypress/code-coverage/task')(on, config)
      // include any other plugin code...

      // It's IMPORTANT to return the config object
      // with any changed environment variables
      return config
    },
  },
  env: {
    landing_page: '/landing-page',
    login_page: '/login',
    recover_page: '/recover',
    hedy_page: '/hedy',
    hedy_level2_page: '/hedy/2',
    hedy_level5_page: '/hedy/5',
    adventure_page: '/hedy/1#print_command',
    admin_page: '/admin',
    admin_users_page: '/admin/users',
    teachers_page: '/for-teachers',
    class_page: '/for-teachers/class/',
    customize_class_page: '/for-teachers/customize-class/', // You should concatenate this with the class id e.g. /for-teachers/customize_class/<class id>
    stats_page: '/stats/class/', // You should concatenate this with the class id e.g. /stats/class/<class id>
    logs_page: '/logs/class/', // You should concatenate this with the class id e.g. /logs/class/<class id>
    grid_overview_page: '/grid_overview/class', 
    register_student_page: '/signup?teacher=false',
    register_teacher_page: '/signup?teacher=true',
    profile_page: '/my-profile',
    admin_page: '/admin',
    admin_stats_page: '/admin/stats',
    admin_adventures_page: '/admin/adventures',
    admin_achievements_page: '/admin/achievements',
    admin_classes_page: '/admin/classes',
    programs_page: '/programs',
    explore_programs_page: '/explore',
  }
});
