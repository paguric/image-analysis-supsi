import TEXT from '../constants/Info';

function TextRetriever({ label }) {
    return (
        <span
            dangerouslySetInnerHTML={{ __html: TEXT[label] }}
        />
    );
}

export default TextRetriever;