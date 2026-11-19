import { Hono } from 'hono';
import { reddit } from '@devvit/web/server';

// Prueba pequeña y exclusivamente de lectura.
// No guarda datos, no envía contenido fuera de Reddit y no llama a ningún modelo de IA.
export const radarPilot = new Hono();

radarPilot.get('/radar-pilot', async (c) => {
  const communities = ['ChatGPT', 'sysadmin'] as const;
  const result = [];
  const cutoff = Date.now() - 7 * 24 * 60 * 60 * 1000;

  for (const community of communities) {
    try {
      const list = await reddit.getNewPosts({
        subredditName: community,
        limit: 20,
        pageSize: 20,
      }).all();

      const posts = [];
      for (const post of list.filter(p => p.createdAt.getTime() >= cutoff).slice(0, 3)) {
        let comments: { text: string; score: number }[] = [];
        let commentsError: string | undefined;

        try {
          const firstComments = await reddit.getComments({
            postId: post.id,
            limit: 3,
            pageSize: 3,
          }).all();
          comments = firstComments
            .filter(comment => Boolean(comment.body))
            .slice(0, 2)
            .map(comment => ({ text: comment.body.slice(0, 280), score: comment.score }));
        } catch (error) {
          commentsError = error instanceof Error ? error.message : String(error);
        }

        posts.push({
          title: post.title,
          url: `https://www.reddit.com${post.permalink}`,
          created: post.createdAt.toISOString(),
          score: post.score,
          commentCount: post.numberOfComments,
          comments,
          ...(commentsError ? { commentsError } : {}),
        });
      }
      result.push({ community, status: 'ok', posts });
    } catch (error) {
      result.push({
        community,
        status: 'error',
        message: error instanceof Error ? error.message : String(error),
      });
    }
  }

  return c.json({ mode: 'devvit-read-only', dataStored: false, communities: result });
});
