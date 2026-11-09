# Adds the HoneyWidgets extension (lock-screen timers, later home-screen widgets) to the Xcode project.
# Safe to run more than once.
require 'xcodeproj'
proj = Xcodeproj::Project.open(File.join(__dir__, '..', 'ios', 'App', 'App.xcodeproj'))
app = proj.targets.find { |t| t.name == 'App' }
appgrp = proj.main_group.children.find { |g| g.respond_to?(:path) && g.path == 'App' } or abort 'App group not found'

# app-side files
%w[HoneyActivity.swift HoneyNative.swift MainViewController.swift].each do |f|
  next if appgrp.files.any? { |r| r.path == f }
  ref = appgrp.new_reference(f)
  app.add_file_references([ref])
end
app.build_configurations.each do |c|
  flags = Array(c.build_settings['OTHER_LDFLAGS'] || ['$(inherited)'])
  flags = flags.flat_map { |x| x.split(' ') }
  flags += ['-weak_framework', 'ActivityKit'] unless flags.include?('ActivityKit')
  c.build_settings['OTHER_LDFLAGS'] = flags
end

unless proj.targets.any? { |t| t.name == 'HoneyWidgets' }
  ext = proj.new_target(:app_extension, 'HoneyWidgets', :ios, '16.2', nil, :swift)
  grp = proj.main_group.new_group('HoneyWidgets', 'HoneyWidgets')
  %w[HoneyWidgetsBundle.swift HoneyLiveActivity.swift].each { |f| ext.add_file_references([grp.new_reference(f)]) }
  grp.new_reference('Info.plist')
  shared = appgrp.files.find { |r| r.path == 'HoneyActivity.swift' }
  ext.add_file_references([shared])
  ext.build_configurations.each do |c|
    s = c.build_settings
    s['PRODUCT_BUNDLE_IDENTIFIER'] = 'com.honeybeebaby.app.widgets'
    s['PRODUCT_NAME'] = '$(TARGET_NAME)'
    s['INFOPLIST_FILE'] = 'HoneyWidgets/Info.plist'
    s['GENERATE_INFOPLIST_FILE'] = 'NO'
    s['SWIFT_VERSION'] = '5.0'
    s['TARGETED_DEVICE_FAMILY'] = '1,2'
    s['IPHONEOS_DEPLOYMENT_TARGET'] = '16.2'
    s['MARKETING_VERSION'] = '1.0'
    s['CURRENT_PROJECT_VERSION'] = '1'
    s['SKIP_INSTALL'] = 'YES'
    s['CODE_SIGN_STYLE'] = 'Automatic'
    s['LD_RUNPATH_SEARCH_PATHS'] = ['$(inherited)', '@executable_path/Frameworks', '@executable_path/../../Frameworks']
    s['ASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME'] = ''
  end
  embed = app.new_copy_files_build_phase('Embed Foundation Extensions')
  embed.symbol_dst_subfolder_spec = :plug_ins
  bf = embed.add_file_reference(ext.product_reference, true)
  bf.settings = { 'ATTRIBUTES' => ['RemoveHeadersOnCopy'] }
  app.add_dependency(ext)
end
proj.save
puts 'HoneyWidgets target ready'
