import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';

mermaid.initialize({
    startOnLoad: true,
    theme: 'default',
    securityLevel: 'loose',
    fontFamily: 'sans-serif'
});

const MermaidDiagram = ({ chart }) => {
    const containerRef = useRef(null);
    const [svg, setSvg] = useState('');

    useEffect(() => {
        const renderDiagram = async () => {
            if (chart) {
                try {
                    const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`;
                    const { svg } = await mermaid.render(id, chart);
                    setSvg(svg);
                } catch (e) {
                    console.error('Mermaid rendering error:', e);
                    setSvg('<div style="color:red">Failed to render diagram</div>');
                }
            }
        };
        renderDiagram();
    }, [chart]);

    return (
        <div
            ref={containerRef}
            className="mermaid"
            style={{
                display: 'flex',
                justifyContent: 'center',
                padding: '20px',
                background: '#fff',
                borderRadius: '8px',
                overflowX: 'auto'
            }}
            dangerouslySetInnerHTML={{ __html: svg }}
        />
    );
};

export default MermaidDiagram;
