import TEXT from '../constants/PageInfos';

function TextRetriever({ label }) {
    const content = TEXT[label] ?? label;

    return (
        <div
            dangerouslySetInnerHTML={{ __html: content }}
        />
    );
}

export default TextRetriever;