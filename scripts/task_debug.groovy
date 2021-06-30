import org.sonatype.nexus.scheduling.TaskScheduler

TaskScheduler taskScheduler = container.lookup(TaskScheduler.class.getName())
log.info('{}', taskScheduler.listsTasks())
