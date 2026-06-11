<?php
$db_path = '/var/www/data/guestbook.db';
$db = new PDO('sqlite:' . $db_path);
$db->exec('CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at INTEGER NOT NULL
)');

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $author  = trim($_POST['author'] ?? '');
    $content = trim($_POST['content'] ?? '');
    if ($author !== '' && $content !== ''
        && mb_strlen($author) <= 32 && mb_strlen($content) <= 500) {
        $stmt = $db->prepare(
            'INSERT INTO messages (author, content, created_at) VALUES (?, ?, ?)'
        );
        $stmt->execute([$author, $content, time()]);
    }
    header('Location: /guestbook/');
    exit;
}

$messages = $db->query(
    'SELECT * FROM messages ORDER BY id DESC LIMIT 50'
)->fetchAll(PDO::FETCH_ASSOC);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ft_onion — guestbook</title>
    <link rel="stylesheet" href="/guestbook/style.css">
</head>
<body>
    <main>
        <h1>ft_onion</h1>
        <p class="sub">Anonymous guestbook on the Tor network.</p>

        <form method="POST" action="/guestbook/">
            <input type="text" name="author" placeholder="Name" maxlength="32" required>
            <textarea name="content" placeholder="Your message..." maxlength="500" rows="3" required></textarea>
            <button type="submit">Sign</button>
        </form>

        <section class="messages">
            <?php if (empty($messages)): ?>
                <p class="empty">No messages yet. Be the first.</p>
            <?php else: ?>
                <?php foreach ($messages as $m): ?>
                    <article>
                        <header>
                            <strong><?= htmlspecialchars($m['author']) ?></strong>
                            <time><?= date('Y-m-d H:i', $m['created_at']) ?></time>
                        </header>
                        <p><?= nl2br(htmlspecialchars($m['content'])) ?></p>
                    </article>
                <?php endforeach; ?>
            <?php endif; ?>
        </section>
    </main>
</body>
</html>
