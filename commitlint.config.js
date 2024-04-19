module.exports = {
  /**
   * Resolve and load @commitlint/config-conventional from node_modules.
   * Referenced packages must be installed
   */
  extends: ["@commitlint/config-conventional"],
  /**
   * Resolve and load @commitlint/format from node_modules.
   * Referenced package must be installed
   */
  formatter: "@commitlint/format",
  /**
   * Any rules defined here will override rules from @commitlint/config-conventional
   */
  rules: {
    "scope-enum": [
      2,
      "always",
      [
        "server",
        "component_manager",
        "eventbus",
        "injector",
        "utils",
        "webserver",
        "database",
        "settings_manager",
        "camera",
        "client",
        "storage_manager",
      ],
    ],
  },
};
